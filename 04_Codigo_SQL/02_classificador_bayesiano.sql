-- =====================================================================
-- Classificador Naive Bayes (SQL) - Previsão de Atraso na Entrega
-- Domínio: Logística
-- Requer a tabela treinamento_logistica (ver 01_massa_dados.sql)
-- =====================================================================

-- ETAPA A: Definição do novo caso a ser classificado
-- (troque os valores aqui para testar outro perfil - ver 05_Testes_e_Resultados)
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

-- ETAPA B: contagens base e tamanho do vocabulário de cada feature (para Laplace)
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

-- ETAPA C: probabilidade a priori P(classe), em log
priori AS (
    SELECT
        atraso,
        COUNT(*) AS qtd_classe,
        LN((COUNT(*) * 1.0) / MAX(e.total_registros)) AS log_priori
    FROM treinamento_logistica
    CROSS JOIN estatisticas_base e
    GROUP BY atraso
),

-- ETAPA D: verossimilhanças P(feature=valor | classe) com suavização de Laplace, em log
-- Fórmula de Laplace: (Contagem(feature=valor, classe) + 1) / (Total(classe) + |Vocabulário(feature)|)
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

-- ETAPA E: soma dos logs (evita underflow numérico) e reversão para escala normal (exp)
score_bruto AS (
    SELECT
        atraso,
        (log_priori + log_v_dist + log_v_clima + log_v_veiculo + log_v_transito + log_v_turno + log_v_dia + log_v_carga) AS log_score_final,
        EXP(log_priori + log_v_dist + log_v_clima + log_v_veiculo + log_v_transito + log_v_turno + log_v_dia + log_v_carga) AS score_exp
    FROM verossimilhanca
)

-- ETAPA F: normalização (0% a 100%) + recomendação de decisão
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

