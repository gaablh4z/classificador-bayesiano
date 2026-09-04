# ==============================================================================
# 1. IMPORTAÇÃO DE BIBLIOTECAS
# ==============================================================================
# Importa:
# - sqlite3: motor de banco de dados SQL embutido no Python
# - json: leitura do arquivo de casos de testes e resultados de referência
import sqlite3
import json

# ==============================================================================
# 2. INICIALIZAÇÃO DO BANCO DE DADOS EM MEMÓRIA
# ==============================================================================
# Cria uma instância de banco SQLite em memória RAM (:memory:).
# Não grava arquivos em disco, sendo muito rápido para testes automatizados.
conn = sqlite3.connect(":memory:")

# ==============================================================================
# 3. CARGA DA MASSA DE TREINAMENTO NO BANCO
# ==============================================================================
# Abre o arquivo SQL que cria a tabela e insere todos os 240 registros de treino.
# Executa todo o script SQL dentro da base em memória.
with open("04_Codigo_SQL/01_massa_dados.sql", "r", encoding="utf-8") as f:
    conn.executescript(f.read())

# ==============================================================================
# 4. CONFERÊNCIA DOS DADOS INSERIDOS
# ==============================================================================
# Faz uma contagem rápida agrupada pela coluna 'atraso' para confirmar
# se os 240 registros foram inseridos corretamente (162 'Não' e 78 'Sim').
cur = conn.cursor()
cur.execute("SELECT count(*), atraso FROM treinamento_logistica GROUP BY atraso")
print("Dados no banco:", cur.fetchall())

# ==============================================================================
# 5. CARREGAMENTO DA CONSULTA SQL DO CLASSIFICADOR BAYESIANO
# ==============================================================================
# Lê o arquivo com a consulta SQL que implementa a lógica do Naive Bayes
# com cálculo em escala logarítmica, correção de Laplace e normalização softmax.
with open("04_Codigo_SQL/02_classificador_bayesiano.sql", "r", encoding="utf-8") as f:
    sql_query = f.read()

# ==============================================================================
# 6. LEITURA DOS CENÁRIOS DE TESTE E RESULTADOS ESPERADOS
# ==============================================================================
# Lê o arquivo JSON com a definição dos 6 cenários de teste (perfil de entrega)
# e as saídas esperadas (scores e probabilidades pré-calculadas).
with open("05_Testes_e_Resultados/resultados_brutos.json", "r", encoding="utf-8") as f:
    casos = json.load(f)

# ==============================================================================
# 7. EXECUÇÃO DOS TESTES E COMPARAÇÃO DOS RESULTADOS
# ==============================================================================
# Para cada um dos 6 casos de teste:
# 1. Passa as características da entrega como parâmetros da query SQL;
# 2. Executa a inferência Bayesiana dentro do banco SQLite;
# 3. Exibe a classe predita, log-score, probabilidade e recomendação;
# 4. Compara com a referência esperada para validar a precisão matemática.
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
    
    # Dicionário com os valores de referência esperados: classe -> (log_score, probabilidade)
    expected = {r[0]: (r[1], r[2]) for r in c["linhas"]}
    for row in rows:
        cls = row[0]
        exp_log, exp_prob = expected[cls]
        # Verifica se a diferença numérica está dentro de uma tolerância mínima
        if abs(row[1] - exp_log) > 0.01 or abs(row[2] - exp_prob) > 0.05:
            print(f"  [DIVERGENCIA] {cls}: obtido ({row[1]}, {row[2]}) vs esperado ({exp_log}, {exp_prob})")
            all_matched = False

# ==============================================================================
# 8. EXIBIÇÃO DO VEREDITO FINAL DOS TESTES
# ==============================================================================
# Informa se todos os cenários foram validados com 100% de conformidade.
if all_matched:
    print("\nTODOS OS 6 CASOS DE TESTE BATERAM 100% COM OS RESULTADOS ESPERADOS!")
else:
    print("\nHOUVE DIVERGÊNCIAS NOS RESULTADOS!")
