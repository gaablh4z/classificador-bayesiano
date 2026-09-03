import sqlite3
import json

conn = sqlite3.connect(":memory:")

# Load training data
with open("04_Codigo_SQL/01_massa_dados.sql", "r", encoding="utf-8") as f:
    conn.executescript(f.read())

cur = conn.cursor()
cur.execute("SELECT count(*), atraso FROM treinamento_logistica GROUP BY atraso")
print("Dados no banco:", cur.fetchall())

with open("04_Codigo_SQL/02_classificador_bayesiano.sql", "r", encoding="utf-8") as f:
    sql_query = f.read()

with open("05_Testes_e_Resultados/resultados_brutos.json", "r", encoding="utf-8") as f:
    casos = json.load(f)

print("\n--- Validando os 6 Casos de Teste ---")
all_matched = True
for c in casos:
    nome = c["caso"]
    perfil = c["perfil"]
    cur.execute(sql_query, perfil)
    rows = cur.fetchall()
    print(f"\nCaso: {nome}")
    for row in rows:
        print(f"  Classe: {row[0]}, Log_Score: {row[1]}, Prob: {row[2]}%, Rec: {row[3][:40]}...")
    
    # Compare with expected in c["linhas"]
    # expected: [["Sim", -6.6739, 98.9, "..."], ["Não", -11.1703, 1.1, ""]]
    expected = {r[0]: (r[1], r[2]) for r in c["linhas"]}
    for row in rows:
        cls = row[0]
        exp_log, exp_prob = expected[cls]
        if abs(row[1] - exp_log) > 0.01 or abs(row[2] - exp_prob) > 0.05:
            print(f"  [DIVERGENCIA] {cls}: obtido ({row[1]}, {row[2]}) vs esperado ({exp_log}, {exp_prob})")
            all_matched = False

if all_matched:
    print("\nTODOS OS 6 CASOS DE TESTE BATERAM 100% COM OS RESULTADOS ESPERADOS!")
else:
    print("\nHOUVE DIVERGÊNCIAS NOS RESULTADOS!")
