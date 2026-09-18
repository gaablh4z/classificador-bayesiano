"""
Script de Execução e Validação dos Testes - Domínio Agronegócio
Executa o classificador Naive Bayes em SQL puro (02_classificador_bayesiano.sql)
dentro do SQLite, avalia os 5 casos de teste e salva os resultados em 05_Testes_e_Resultados/
"""

import sqlite3
import json
import csv
import math
from pathlib import Path

# Definição dos 5 cenários de teste exigidos na Etapa 4
CASOS_TESTE = [
    {
        "cenario_id": 1,
        "nome": "Baixo Risco (Planalto irrigado em outubro)",
        "perfil": {
            "v_tipo_solo": "argiloso",
            "v_seca": "nenhuma",
            "v_chuva": "normal",
            "v_mes_plantio": "outubro",
            "v_irrigacao": "irrigado",
            "v_pragas": "baixa",
            "v_regiao": "planalto",
        },
        "esperado": "Não (Risco < 5%)",
    },
    {
        "cenario_id": 2,
        "nome": "Alto Risco Extremo (Solo arenoso, seca severa, plantio em dezembro)",
        "perfil": {
            "v_tipo_solo": "arenoso",
            "v_seca": "severa",
            "v_chuva": "pouca",
            "v_mes_plantio": "dezembro",
            "v_irrigacao": "convencional",
            "v_pragas": "alta",
            "v_regiao": "baixada",
        },
        "esperado": "Sim (Risco > 90%)",
    },
    {
        "cenario_id": 3,
        "nome": "Dilema da Irrigação (Solo arenoso compensado por pivô)",
        "perfil": {
            "v_tipo_solo": "arenoso",
            "v_seca": "nenhuma",
            "v_chuva": "normal",
            "v_mes_plantio": "novembro",
            "v_irrigacao": "irrigado",
            "v_pragas": "media",
            "v_regiao": "transicao",
        },
        "esperado": "Não (Tecnologia compensa solo)",
    },
    {
        "cenario_id": 4,
        "nome": "Resiliência da Argila (Solo argiloso sob seca severa)",
        "perfil": {
            "v_tipo_solo": "argiloso",
            "v_seca": "severa",
            "v_chuva": "pouca",
            "v_mes_plantio": "outubro",
            "v_irrigacao": "plantio_direto",
            "v_pragas": "media",
            "v_regiao": "planalto",
        },
        "esperado": "Não (Risco moderado ~30-40% graças à microporosidade)",
    },
    {
        "cenario_id": 5,
        "nome": "Teste de Laplace (Solo inédito fora do treinamento)",
        "perfil": {
            "v_tipo_solo": "solo_desconhecido",
            "v_seca": "moderada",
            "v_chuva": "normal",
            "v_mes_plantio": "novembro",
            "v_irrigacao": "plantio_direto",
            "v_pragas": "baixa",
            "v_regiao": "transicao",
        },
        "esperado": "Não quebra por divisão por zero (Laplace ativo)",
    },
]


def main():
    dir_atual = Path(__file__).resolve().parent
    dir_raiz = dir_atual.parent
    dir_resultados = dir_raiz / "05_Testes_e_Resultados"
    dir_resultados.mkdir(parents=True, exist_ok=True)

    caminho_massa = dir_atual / "01_massa_dados.sql"
    caminho_query = dir_atual / "02_classificador_bayesiano.sql"

    print("=" * 75)
    print(" EXECUÇÃO DO CLASSIFICADOR NAIVE BAYES EM SQL PURO (ETAPAS 3 E 4) ")
    print("=" * 75)

    # 1. Carregar banco SQLite (direto do arquivo pré-indexado ou via script DDL+INSERTs)
    caminho_db = dir_raiz / "03_Dataset" / "safra_treinamento.db"
    if caminho_db.exists():
        conn = sqlite3.connect(caminho_db)
        cur = conn.cursor()
    else:
        conn = sqlite3.connect(":memory:")
        cur = conn.cursor()
        with open(caminho_massa, "r", encoding="utf-8") as f:
            conn.executescript(f.read())

    cur.execute("SELECT perda_safra, COUNT(*) FROM talhoes GROUP BY perda_safra;")
    distribuicao = dict(cur.fetchall())
    print(f"Base de treinamento carregada: {distribuicao}")

    # 2. Carregar consulta SQL do Naive Bayes
    with open(caminho_query, "r", encoding="utf-8") as f:
        sql_query = f.read()

    # 3. Executar os 5 cenários de teste
    resultados_brutos = []
    print("\n" + "-" * 75)
    print(f"{'#':<3} | {'Cenário':<42} | {'Classe':<6} | {'Prob':<8} | {'Log-Score':<10}")
    print("-" * 75)

    for c in CASOS_TESTE:
        cid = c["cenario_id"]
        nome = c["nome"]
        perfil = c["perfil"]

        cur.execute(sql_query, perfil)
        linhas = cur.fetchall()

        vencedor = linhas[0]
        classe_pred = vencedor[0]
        log_score = vencedor[1]
        prob_venc = vencedor[2]
        recomendacao = vencedor[3]

        print(f"{cid:<3} | {nome[:42]:<42} | {classe_pred:<6} | {prob_venc:>5.2f}% | {log_score:>9.4f}")

        detalhe_linhas = [
            {"classe": r[0], "log_score": r[1], "probabilidade": r[2], "recomendacao": r[3]}
            for r in linhas
        ]

        resultados_brutos.append({
            "cenario_id": cid,
            "nome": nome,
            "perfil": perfil,
            "esperado": c["esperado"],
            "classe_predita": classe_pred,
            "prob_vencedora": prob_venc,
            "detalhes": detalhe_linhas,
        })

    print("-" * 75)

    # 4. Calcular Poder Discriminativo das Features (Log-Odds)
    # Log-Odds = ln( P(feature=valor | Sim) / P(feature=valor | Não) )
    print("\nCalculando poder discriminativo (Log-Odds) das features...")
    features = ["tipo_solo", "seca", "chuva", "mes_plantio", "irrigacao", "pragas", "regiao"]
    
    cur.execute("SELECT COUNT(*) FROM talhoes WHERE perda_safra = 'Sim'")
    total_sim = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM talhoes WHERE perda_safra = 'Não'")
    total_nao = cur.fetchone()[0]

    ranking_log_odds = []

    for feat in features:
        cur.execute(f"SELECT COUNT(DISTINCT {feat}) FROM talhoes")
        v_i = cur.fetchone()[0]

        cur.execute(f"SELECT DISTINCT {feat} FROM talhoes")
        categorias = [row[0] for row in cur.fetchall()]

        for cat in categorias:
            cur.execute(f"SELECT COUNT(*) FROM talhoes WHERE {feat} = ? AND perda_safra = 'Sim'", (cat,))
            cnt_sim = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(*) FROM talhoes WHERE {feat} = ? AND perda_safra = 'Não'", (cat,))
            cnt_nao = cur.fetchone()[0]

            # Laplace
            p_sim = (cnt_sim + 1.0) / (total_sim + v_i)
            p_nao = (cnt_nao + 1.0) / (total_nao + v_i)

            log_odds = math.log(p_sim / p_nao)

            ranking_log_odds.append({
                "feature": feat,
                "categoria": cat,
                "p_sim": round(p_sim, 4),
                "p_nao": round(p_nao, 4),
                "log_odds": round(log_odds, 4),
                "poder_discriminativo_abs": round(abs(log_odds), 4),
            })

    ranking_log_odds.sort(key=lambda x: x["poder_discriminativo_abs"], reverse=True)

    # 5. Salvar arquivos em 05_Testes_e_Resultados
    caminho_json = dir_resultados / "resultados_brutos.json"
    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(resultados_brutos, f, indent=2, ensure_ascii=False)

    caminho_logodds = dir_resultados / "log_odds.json"
    with open(caminho_logodds, "w", encoding="utf-8") as f:
        json.dump(ranking_log_odds, f, indent=2, ensure_ascii=False)

    caminho_casos_csv = dir_resultados / "casos_teste.csv"
    with open(caminho_casos_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "cenario_id", "nome", "tipo_solo", "seca", "chuva",
            "mes_plantio", "irrigacao", "pragas", "regiao", "esperado"
        ])
        for c in CASOS_TESTE:
            p = c["perfil"]
            writer.writerow([
                c["cenario_id"], c["nome"], p["v_tipo_solo"], p["v_seca"], p["v_chuva"],
                p["v_mes_plantio"], p["v_irrigacao"], p["v_pragas"], p["v_regiao"], c["esperado"]
            ])

    print(f"\n[OK] Resultados gravados em 05_Testes_e_Resultados/:")
    print(f"  • {caminho_json}")
    print(f"  • {caminho_logodds}")
    print(f"  • {caminho_casos_csv}")

    # Top 5 maiores separadores
    print("\nTop 5 categorias com maior poder discriminativo (|Log-Odds|):")
    for r in ranking_log_odds[:5]:
        direcao = "Aumenta risco de Perda" if r["log_odds"] > 0 else "Indica Safra Regular"
        print(f"  - {r['feature']} = '{r['categoria']}': Log-Odds = {r['log_odds']:+.4f} ({direcao})")


if __name__ == "__main__":
    main()
