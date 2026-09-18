-- ==============================================================================
-- ETAPA A: DEFINIÇÃO DO NOVO CASO A SER CLASSIFICADO (ENTRADA)
-- ==============================================================================
WITH novo_caso AS (
    SELECT
        :v_tipo_solo    AS v_tipo_solo,
        :v_seca         AS v_seca,
        :v_chuva        AS v_chuva,
        :v_mes_plantio  AS v_mes_plantio,
        :v_irrigacao    AS v_irrigacao,
        :v_pragas       AS v_pragas,
        :v_regiao       AS v_regiao
),

-- ==============================================================================
-- ETAPA B: CONTAGEM DE TOTAIS E CARDINALIDADES DOS VOCABULÁRIOS (|Vi|)
-- ==============================================================================
estatisticas_base AS (
    SELECT
        COUNT(*) AS total_registros,
        (SELECT COUNT(DISTINCT tipo_solo)   FROM talhoes) AS V_solo,
        (SELECT COUNT(DISTINCT seca)        FROM talhoes) AS V_seca,
        (SELECT COUNT(DISTINCT chuva)       FROM talhoes) AS V_chuva,
        (SELECT COUNT(DISTINCT mes_plantio) FROM talhoes) AS V_mes,
        (SELECT COUNT(DISTINCT irrigacao)   FROM talhoes) AS V_irrig,
        (SELECT COUNT(DISTINCT pragas)      FROM talhoes) AS V_pragas,
        (SELECT COUNT(DISTINCT regiao)      FROM talhoes) AS V_regiao
    FROM talhoes
),

-- ==============================================================================
-- ETAPA C: CÁLCULO DA PROBABILIDADE A PRIORI: P(Classe)
-- ==============================================================================
priori AS (
    SELECT
        perda_safra,
        COUNT(*) AS qtd_classe,
        LN((COUNT(*) * 1.0) / MAX(e.total_registros)) AS log_priori
    FROM talhoes
    CROSS JOIN estatisticas_base e
    GROUP BY perda_safra
),

-- ==============================================================================
-- ETAPA D: CÁLCULO DAS VEROSSIMILHANÇAS COM SUAVIZAÇÃO DE LAPLACE: P(Feature | Classe)
-- ==============================================================================
verossimilhanca AS (
    SELECT
        p.perda_safra,
        p.log_priori,
        p.qtd_classe,
        LN((SUM(CASE WHEN t.tipo_solo   = nc.v_tipo_solo   THEN 1 ELSE 0 END) + 1.0) / (p.qtd_classe + e.V_solo))   AS log_v_solo,
        LN((SUM(CASE WHEN t.seca        = nc.v_seca        THEN 1 ELSE 0 END) + 1.0) / (p.qtd_classe + e.V_seca))   AS log_v_seca,
        LN((SUM(CASE WHEN t.chuva       = nc.v_chuva       THEN 1 ELSE 0 END) + 1.0) / (p.qtd_classe + e.V_chuva))  AS log_v_chuva,
        LN((SUM(CASE WHEN t.mes_plantio = nc.v_mes_plantio THEN 1 ELSE 0 END) + 1.0) / (p.qtd_classe + e.V_mes))    AS log_v_mes,
        LN((SUM(CASE WHEN t.irrigacao   = nc.v_irrigacao   THEN 1 ELSE 0 END) + 1.0) / (p.qtd_classe + e.V_irrig))  AS log_v_irrig,
        LN((SUM(CASE WHEN t.pragas      = nc.v_pragas      THEN 1 ELSE 0 END) + 1.0) / (p.qtd_classe + e.V_pragas)) AS log_v_pragas,
        LN((SUM(CASE WHEN t.regiao      = nc.v_regiao      THEN 1 ELSE 0 END) + 1.0) / (p.qtd_classe + e.V_regiao)) AS log_v_regiao
    FROM priori p
    LEFT JOIN talhoes t ON p.perda_safra = t.perda_safra
    CROSS JOIN novo_caso nc
    CROSS JOIN estatisticas_base e
    GROUP BY p.perda_safra, p.log_priori, p.qtd_classe, e.V_solo, e.V_seca, e.V_chuva,
             e.V_mes, e.V_irrig, e.V_pragas, e.V_regiao
),

-- ==============================================================================
-- ETAPA E: COMBINAÇÃO DAS EVIDÊNCIAS E CONVERSÃO EXPONENCIAL
-- ==============================================================================
score_bruto AS (
    SELECT
        perda_safra,
        (log_priori + log_v_solo + log_v_seca + log_v_chuva + log_v_mes + log_v_irrig + log_v_pragas + log_v_regiao) AS log_score_final,
        EXP(log_priori + log_v_solo + log_v_seca + log_v_chuva + log_v_mes + log_v_irrig + log_v_pragas + log_v_regiao) AS score_exp
    FROM verossimilhanca
)

-- ==============================================================================
-- ETAPA F: NORMALIZAÇÃO PERCENTUAL (0% a 100%) E TOMADA DE DECISÃO
-- ==============================================================================
SELECT
    perda_safra AS Classe,
    ROUND(log_score_final, 4) AS Log_Score,
    ROUND((score_exp / SUM(score_exp) OVER()) * 100, 2) AS Probabilidade_Percentual,
    CASE
        WHEN perda_safra = 'Sim'
             AND (score_exp / SUM(score_exp) OVER()) * 100 >= 50.0
        THEN 'RECOMENDAÇÃO: Alto risco de quebra de safra. Exigir garantia real / acionar apólice de seguro agrícola.'
        WHEN perda_safra = 'Não'
             AND (score_exp / SUM(score_exp) OVER()) * 100 >= 50.0
        THEN 'RECOMENDAÇÃO: Baixo risco de quebra. Liberar crédito de custeio / safra regular esperada.'
        ELSE ''
    END AS Recomendacao
FROM score_bruto
ORDER BY Probabilidade_Percentual DESC;
