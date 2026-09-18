"""
Script de Geração da Massa de Dados de Treinamento - Domínio Agronegócio
Gera dados sintéticos de talhões agrícolas com regras probabilísticas realistas
e nomes de features simplificados, conforme a Etapa 2 da Atividade Prática 1.

Saídas:
  - 03_Dataset/safra_treinamento.csv
  - 03_Dataset/safra_treinamento.sql
  - 03_Dataset/safra_treinamento.db
  - 04_Codigo_SQL/01_massa_dados.sql
"""

import os
import csv
import math
import random
import sqlite3
import shutil
from pathlib import Path

SEED = 42
TOTAL_REGISTROS = 200_000  # Quantidade solicitada: 200 mil registros de alta fidelidade estatística

# Categorias das 7 features simplificadas
OPCOES = {
    "tipo_solo": ["argiloso", "medio", "arenoso"],
    "seca": ["nenhuma", "moderada", "severa"],
    "chuva": ["normal", "excessiva", "pouca"],
    "mes_plantio": ["outubro", "novembro", "dezembro"],
    "irrigacao": ["plantio_direto", "convencional", "irrigado"],
    "pragas": ["baixa", "media", "alta"],
    "regiao": ["planalto", "transicao", "baixada"],
}

PESOS_FREQUENCIA = {
    "tipo_solo": [0.50, 0.25, 0.25],
    "seca": [0.52, 0.28, 0.20],
    "chuva": [0.55, 0.15, 0.30],
    "mes_plantio": [0.50, 0.35, 0.15],
    "irrigacao": [0.70, 0.18, 0.12],
    "pragas": [0.35, 0.45, 0.20],
    "regiao": [0.45, 0.35, 0.20],
}

PESOS_RISCO = {
    "argiloso": -1.2, "medio": 0.1, "arenoso": 1.4,
    "nenhuma": -1.6, "moderada": 0.1, "severa": 2.4,
    "normal": -1.3, "excessiva": 0.5, "pouca": 1.8,
    "outubro": -0.9, "novembro": 0.2, "dezembro": 1.3,
    "irrigado": -2.0, "plantio_direto": -0.5, "convencional": 1.0,
    "baixa": -1.0, "media": 0.1, "alta": 1.6,
    "planalto": -0.7, "transicao": 0.0, "baixada": 0.8,
}

INTERCEPTO = -1.6


def calcular_probabilidade_perda(dados: dict) -> float:
    z = INTERCEPTO
    for v in dados.values():
        if v in PESOS_RISCO:
            z += PESOS_RISCO[v]

    # Interações não-lineares intencionais do mundo real
    if dados["tipo_solo"] == "arenoso" and dados["seca"] == "severa":
        z += 1.2
    if dados["irrigacao"] == "irrigado" and dados["chuva"] == "pouca":
        z -= 1.0

    return 1.0 / (1.0 + math.exp(-z))


def gerar_amostra() -> dict:
    reg = {k: random.choices(OPCOES[k], weights=PESOS_FREQUENCIA[k])[0] for k in OPCOES}
    prob = calcular_probabilidade_perda(reg)
    reg["perda_safra"] = "Sim" if random.random() < prob else "Não"
    return reg


def main(total: int = TOTAL_REGISTROS):
    random.seed(SEED)
    dir_dataset = Path(__file__).resolve().parent
    dir_codigo_sql = dir_dataset.parent / "04_Codigo_SQL"
    dir_codigo_sql.mkdir(parents=True, exist_ok=True)

    caminho_csv = dir_dataset / "safra_treinamento.csv"
    caminho_sql = dir_dataset / "safra_treinamento.sql"
    caminho_db = dir_dataset / "safra_treinamento.db"
    caminho_massa_sql = dir_codigo_sql / "01_massa_dados.sql"

    colunas = ["tipo_solo", "seca", "chuva", "mes_plantio", "irrigacao", "pragas", "regiao", "perda_safra"]

    print(f"Gerando {total} registros de treinamento agronômico...")
    registros = [gerar_amostra() for _ in range(total)]

    # 1. Salvar CSV
    with open(caminho_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=colunas)
        writer.writeheader()
        writer.writerows(registros)

    # 2. Salvar SQL
    with open(caminho_sql, mode="w", encoding="utf-8") as f:
        f.write("-- ==============================================================================\n")
        f.write("-- MASSA DE DADOS DE TREINAMENTO: AGRONEGÓCIO (RISCO DE PERDA DE SAFRA)\n")
        f.write(f"-- Total de Registros: {total} amostras calibradas com padrões agronômicos\n")
        f.write("-- ==============================================================================\n\n")
        f.write("DROP TABLE IF EXISTS talhoes;\n\n")
        f.write("CREATE TABLE talhoes (\n")
        f.write("    id INTEGER PRIMARY KEY AUTOINCREMENT,\n")
        f.write("    tipo_solo TEXT NOT NULL,\n")
        f.write("    seca TEXT NOT NULL,\n")
        f.write("    chuva TEXT NOT NULL,\n")
        f.write("    mes_plantio TEXT NOT NULL,\n")
        f.write("    irrigacao TEXT NOT NULL,\n")
        f.write("    pragas TEXT NOT NULL,\n")
        f.write("    regiao TEXT NOT NULL,\n")
        f.write("    perda_safra TEXT NOT NULL\n")
        f.write(");\n\n")
        f.write("BEGIN TRANSACTION;\n")
        lines = [f"INSERT INTO talhoes ({', '.join(colunas)}) VALUES ({', '.join(repr(r[c]) for c in colunas)});\n" for r in registros]
        f.writelines(lines)
        f.write("COMMIT;\n\n")
        f.write("CREATE INDEX IF NOT EXISTS idx_perda ON talhoes(perda_safra);\n")
        f.write("CREATE INDEX IF NOT EXISTS idx_solo ON talhoes(tipo_solo);\n")
        f.write("CREATE INDEX IF NOT EXISTS idx_seca ON talhoes(seca);\n")
        f.write("CREATE INDEX IF NOT EXISTS idx_chuva ON talhoes(chuva);\n")
        f.write("CREATE INDEX IF NOT EXISTS idx_mes ON talhoes(mes_plantio);\n")
        f.write("CREATE INDEX IF NOT EXISTS idx_irrig ON talhoes(irrigacao);\n")
        f.write("CREATE INDEX IF NOT EXISTS idx_pragas ON talhoes(pragas);\n")
        f.write("CREATE INDEX IF NOT EXISTS idx_regiao ON talhoes(regiao);\n")

    # Copiar script para 04_Codigo_SQL/01_massa_dados.sql
    shutil.copyfile(caminho_sql, caminho_massa_sql)

    # 3. Salvar Banco SQLite
    if caminho_db.exists():
        caminho_db.unlink()
    conn = sqlite3.connect(caminho_db)
    conn.execute("DROP TABLE IF EXISTS talhoes;")
    conn.execute("""
    CREATE TABLE talhoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_solo TEXT NOT NULL,
        seca TEXT NOT NULL,
        chuva TEXT NOT NULL,
        mes_plantio TEXT NOT NULL,
        irrigacao TEXT NOT NULL,
        pragas TEXT NOT NULL,
        regiao TEXT NOT NULL,
        perda_safra TEXT NOT NULL
    );
    """)
    conn.executemany(
        f"INSERT INTO talhoes ({', '.join(colunas)}) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [[r[c] for c in colunas] for r in registros]
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_perda ON talhoes(perda_safra);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_solo ON talhoes(tipo_solo);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_seca ON talhoes(seca);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_chuva ON talhoes(chuva);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_mes ON talhoes(mes_plantio);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_irrig ON talhoes(irrigacao);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_pragas ON talhoes(pragas);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_regiao ON talhoes(regiao);")
    conn.commit()

    # Estatísticas das classes
    cur = conn.cursor()
    cur.execute("SELECT perda_safra, COUNT(*) FROM talhoes GROUP BY perda_safra;")
    stats = dict(cur.fetchall())
    conn.close()

    total_sim = stats.get("Sim", 0)
    total_nao = stats.get("Não", 0)
    pct_sim = (total_sim / total) * 100
    pct_nao = (total_nao / total) * 100

    print(f"[OK] Base de dados gerada com sucesso!")
    print(f"  • CSV:    {caminho_csv}")
    print(f"  • SQL:    {caminho_sql} (e copiado para {caminho_massa_sql})")
    print(f"  • SQLite: {caminho_db}")
    print(f"  • Distribuição das classes: Perda (Sim): {total_sim} ({pct_sim:.1f}%) | Regular (Não): {total_nao} ({pct_nao:.1f}%)")


if __name__ == "__main__":
    main()
