-- ==============================================================================
-- MODELO PREDITIVO NAIVE BAYES IMPLEMENTADO EM SQL PURO
-- Domínio: Previsão de Atraso em Entregas Logísticas
-- Base de Dados: Tabela 'treinamento_logistica' (gerada em 01_massa_dados.sql)
--
-- Visão Geral do Algoritmo:
-- 1. Calcula a chance básica de cada classe ocorrer (Probabilidade a Priori);
-- 2. Calcula a chance de cada característica ocorrer para cada classe (Verossimilhança);
-- 3. Utiliza correção de Laplace para evitar multiplicação por zero em casos inéditos;
-- 4. Trabalha na escala logarítmica (LN) para evitar arredondamentos e perda de precisão;
-- 5. Normaliza os resultados em porcentagem (0% a 100%) e emite recomendação de ação.
-- ==============================================================================

-- ==============================================================================
-- ETAPA A: DEFINIÇÃO DO NOVO CASO A SER CLASSIFICADO (ENTRADA)
-- ==============================================================================
-- Cria uma linha virtual com as características da entrega que desejamos analisar.
-- Os parâmetros com dois-pontos (:v_...) são preenchidos dinamicamente na execução.
WITH novo_caso AS (
    SELECT
        :v_distancia   AS v_distancia,
        :v_clima       AS v_clima,
        :v_veiculo     AS v_veiculo,
        :v_transito    AS v_transito,
        :v_turno       AS v_turno,
        :v_dia_semana  AS v_dia_semana,
        :v_tipo_carga  AS v_tipo_carga
),

-- ==============================================================================
-- ETAPA B: CONTAGEM DE TOTAIS E TAMANHO DO VOCABULÁRIO (|V|)
-- ==============================================================================
-- Conta o total de entregas no histórico e quantos valores distintos existem
-- para cada atributo (ex: 3 tipos de clima, 3 tipos de veículo, etc.).
-- Esses tamanhos de vocabulário (|V|) são exigidos pela fórmula de Laplace no denominador.
estatisticas_base AS (
    SELECT
        COUNT(*) AS total_registros,
        (SELECT COUNT(DISTINCT distancia)  FROM treinamento_logistica) AS V_distancia,
        (SELECT COUNT(DISTINCT clima)      FROM treinamento_logistica) AS V_clima,
        (SELECT COUNT(DISTINCT veiculo)    FROM treinamento_logistica) AS V_veiculo,
        (SELECT COUNT(DISTINCT transito)   FROM treinamento_logistica) AS V_transito,
        (SELECT COUNT(DISTINCT turno)      FROM treinamento_logistica) AS V_turno,
        (SELECT COUNT(DISTINCT dia_semana) FROM treinamento_logistica) AS V_dia_semana,
        (SELECT COUNT(DISTINCT tipo_carga) FROM treinamento_logistica) AS V_carga
    FROM treinamento_logistica
),

-- ==============================================================================
-- ETAPA C: CÁLCULO DA PROBABILIDADE A PRIORI: P(Classe)
-- ==============================================================================
-- Calcula a probabilidade natural de uma entrega atrasar ou não atrasar:
-- P(Sim) = total de 'Sim' / 240
-- P(Não) = total de 'Não' / 240
-- Aplica LN() para converter a probabilidade para escala logarítmica.
priori AS (
    SELECT
        atraso,
        COUNT(*) AS qtd_classe,
        LN((COUNT(*) * 1.0) / MAX(e.total_registros)) AS log_priori
    FROM treinamento_logistica
    CROSS JOIN estatisticas_base e
    GROUP BY atraso
),

-- ==============================================================================
-- ETAPA D: CÁLCULO DAS VEROSSIMILHANÇAS COM SUAVIZAÇÃO DE LAPLACE: P(Atributo | Classe)
-- ==============================================================================
-- Para cada atributo da entrega a ser testada, calcula a chance daquele valor ocorrer na classe.
-- Fórmula de Laplace aplicada em cada termo:
--   P = (Quantidade de vezes que o valor ocorreu na classe + 1) / (Total da classe + |V|)
-- O "+ 1" e o "+ |V|" impedem que qualquer probabilidade vire zero caso um valor
-- nunca tenha sido observado antes no histórico (exemplo: veículo "Drone").
-- O resultado de cada atributo é transformado em logaritmo natural LN().
verossimilhanca AS (
    SELECT
        p.atraso,
        p.log_priori,
        p.qtd_classe,
        LN((SUM(CASE WHEN t.distancia  = nc.v_distancia  THEN 1 ELSE 0 END) + 1.0) / (p.qtd_classe + e.V_distancia))  AS log_v_dist,
        LN((SUM(CASE WHEN t.clima      = nc.v_clima      THEN 1 ELSE 0 END) + 1.0) / (p.qtd_classe + e.V_clima))     AS log_v_clima,
        LN((SUM(CASE WHEN t.veiculo    = nc.v_veiculo    THEN 1 ELSE 0 END) + 1.0) / (p.qtd_classe + e.V_veiculo))   AS log_v_veiculo,
        LN((SUM(CASE WHEN t.transito   = nc.v_transito   THEN 1 ELSE 0 END) + 1.0) / (p.qtd_classe + e.V_transito))  AS log_v_transito,
        LN((SUM(CASE WHEN t.turno      = nc.v_turno      THEN 1 ELSE 0 END) + 1.0) / (p.qtd_classe + e.V_turno))     AS log_v_turno,
        LN((SUM(CASE WHEN t.dia_semana = nc.v_dia_semana THEN 1 ELSE 0 END) + 1.0) / (p.qtd_classe + e.V_dia_semana)) AS log_v_dia,
        LN((SUM(CASE WHEN t.tipo_carga = nc.v_tipo_carga THEN 1 ELSE 0 END) + 1.0) / (p.qtd_classe + e.V_carga))     AS log_v_carga
    FROM priori p
    LEFT JOIN treinamento_logistica t ON p.atraso = t.atraso
    CROSS JOIN novo_caso nc
    CROSS JOIN estatisticas_base e
    GROUP BY p.atraso, p.log_priori, p.qtd_classe, e.V_distancia, e.V_clima, e.V_veiculo,
             e.V_transito, e.V_turno, e.V_dia_semana, e.V_carga
),

-- ==============================================================================
-- ETAPA E: COMBINAÇÃO DAS EVIDÊNCIAS (SOMA DOS LOGS) E CONVERSÃO EXPONENCIAL
-- ==============================================================================
-- No Naive Bayes, as probabilidades são multiplicadas: P(Classe) * P(x1|Classe) * ...
-- Como estamos na escala de logaritmos, a multiplicação vira uma simples soma (evitando underflow).
-- Em seguida, aplicamos EXP() para reverter a soma logarítmica de volta para escala numérica real.
score_bruto AS (
    SELECT
        atraso,
        (log_priori + log_v_dist + log_v_clima + log_v_veiculo + log_v_transito + log_v_turno + log_v_dia + log_v_carga) AS log_score_final,
        EXP(log_priori + log_v_dist + log_v_clima + log_v_veiculo + log_v_transito + log_v_turno + log_v_dia + log_v_carga) AS score_exp
    FROM verossimilhanca
)

-- ==============================================================================
-- ETAPA F: NORMALIZAÇÃO PERCENTUAL (0% a 100%) E TOMADA DE DECISÃO AUTOMÁTICA
-- ==============================================================================
-- Divide o score de cada classe pela soma de todos os scores (normalização Softmax),
-- obtendo a probabilidade percentual exata de cada desfecho.
-- Emite uma recomendação operacional para o time de logística com base na classe vencedora.
SELECT
    atraso AS Classe,
    ROUND(log_score_final, 4) AS Log_Score,
    ROUND((score_exp / SUM(score_exp) OVER()) * 100, 2) AS Probabilidade_Percentual,
    CASE
        WHEN atraso = 'Sim'
             AND (score_exp / SUM(score_exp) OVER()) * 100 = (
                 SELECT MAX(p2) FROM (
                     SELECT (score_exp / SUM(score_exp) OVER()) * 100 AS p2 FROM score_bruto
                 )
             )
        THEN 'RECOMENDAÇÃO: Acionar plano de contingência (troca de modal / priorização) - alto risco de SLA quebrado'
        WHEN atraso = 'Não'
             AND (score_exp / SUM(score_exp) OVER()) * 100 = (
                 SELECT MAX(p2) FROM (
                     SELECT (score_exp / SUM(score_exp) OVER()) * 100 AS p2 FROM score_bruto
                 )
             )
        THEN 'RECOMENDAÇÃO: Manter operação padrão - baixo risco de atraso'
        ELSE ''
    END AS Recomendacao
FROM score_bruto
ORDER BY Probabilidade_Percentual DESC;

