# Atividade Prática 1 — Classificador Bayesiano (Logística)

Previsão de `Atraso_Na_Entrega` (Sim/Não) via Naive Bayes implementado em SQL puro.

## Integrantes da Equipe
- Gabriel Lemos Gomes
- Lucas Peres de Lima

## Estrutura

- **01_Prompts/** — diálogo documentado com a IA em cada etapa (modelagem, dados, código, testes).
- **02_Modelagem/** — Etapa 1: domínio, rótulo, features e discretização.
- **03_Dataset/** — Etapa 2: `treinamento_logistica.csv` (240 registros, 162 Não / 78 Sim) e o script que os gerou (`gerar_dataset.py`).
- **04_Codigo_SQL/** — Etapa 3: `01_massa_dados.sql` (CREATE TABLE + INSERTs), `02_classificador_bayesiano.sql` (o classificador parametrizado) e `executar_testes.py`.
- **05_Testes_e_Resultados/** — Etapa 4: 6 casos de teste **executados de fato** contra o SQL (não estimados), com análise de log-odds.
- **06_Apresentacao/** — Etapa 5: reflexão crítica + roteiro para a defesa oral no VS Code.
- **Atividade/Atividade.pdf** — enunciado original.

## Como rodar o classificador

### Opção 1: Terminal do VS Code (Recomendado para apresentação)
Execute no terminal integrado do VS Code:
```bash
python 04_Codigo_SQL/executar_testes.py
```

### Opção 2: Via Python / SQLite
```python
import sqlite3
conn = sqlite3.connect("dados.db")
conn.executescript(open("04_Codigo_SQL/01_massa_dados.sql", encoding="utf-8").read())
cur = conn.cursor()
cur.execute(open("04_Codigo_SQL/02_classificador_bayesiano.sql", encoding="utf-8").read(), {
    "v_distancia": "Longa", "v_clima": "Tempestade/Alerta", "v_veiculo": "Moto",
    "v_transito": "Severo", "v_turno": "Noite", "v_dia_semana": "Dia Útil",
    "v_tipo_carga": "Frágil/Volume Especial"
})
print(cur.fetchall())
```
