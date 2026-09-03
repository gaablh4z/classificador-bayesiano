# Atividade Prática 1 — Classificador Bayesiano (Logística)

Previsão de `Atraso_Na_Entrega` (Sim/Não) via Naive Bayes implementado em SQL puro.

## Estrutura

- **01_Prompts/** — diálogo documentado com a IA em cada etapa (modelagem, dados, código, testes).
- **02_Modelagem/** — Etapa 1: domínio, rótulo, features e discretização.
- **03_Dataset/** — Etapa 2: `treinamento_logistica.csv` (240 registros, 162 Não / 78 Sim) e o script que os gerou (`gerar_dataset.py`).
- **04_Codigo_SQL/** — Etapa 3: `01_massa_dados.sql` (CREATE TABLE + INSERTs) e `02_classificador_bayesiano.sql` (o classificador, parametrizado por `:v_feature`).
- **05_Testes_e_Resultados/** — Etapa 4: 6 casos de teste **executados de fato** contra o SQL (não estimados), com análise de log-odds.
- **06_Apresentacao/** — Etapa 5: reflexão crítica + roteiro para a defesa oral.
- **Atividade/Atividade.pdf** — enunciado original.

## Como rodar o classificador

O SQL usa parâmetros nomeados (`:v_distancia`, `:v_clima`, etc.), compatível com SQLite,
DuckDB ou qualquer client que suporte bind parameters. Exemplo em Python:

