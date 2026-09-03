"""
Gerador da massa de dados de treinamento - Classificador Bayesiano de Atrasos em Entregas
Domínio: Logística
Gera 240 registros com padrões de risco INTENCIONAIS (não puramente aleatórios),
combinando pesos por feature + regras de interação (ex: Moto + Tempestade agrava o risco).
"""
import random
import csv

random.seed(42)

DISTANCIAS = ["Curta", "Média", "Longa"]
CLIMAS = ["Limpo", "Chuva Leve", "Tempestade/Alerta"]
VEICULOS = ["Moto", "Van", "Caminhão"]
TRANSITOS = ["Leve", "Moderado", "Severo"]
TURNOS = ["Manhã", "Tarde", "Noite"]
DIAS = ["Dia Útil", "Final de Semana/Feriado"]
CARGAS = ["Padrão", "Frágil/Volume Especial"]

PESO_DIST = {"Curta": 0, "Média": 1, "Longa": 2}
PESO_CLIMA = {"Limpo": 0, "Chuva Leve": 1, "Tempestade/Alerta": 3}
PESO_VEIC = {"Caminhão": 0, "Van": 1, "Moto": 2}
PESO_TRANS = {"Leve": 0, "Moderado": 1, "Severo": 3}
PESO_TURNO = {"Manhã": 0, "Tarde": 0, "Noite": 1}
PESO_DIA = {"Dia Útil": 1, "Final de Semana/Feriado": 0}
PESO_CARGA = {"Padrão": 0, "Frágil/Volume Especial": 1}

def risco(distancia, clima, veiculo, transito, turno, dia, carga):
    score = (PESO_DIST[distancia] + PESO_CLIMA[clima] + PESO_VEIC[veiculo] +
             PESO_TRANS[transito] + PESO_TURNO[turno] * 0.5 +
             PESO_DIA[dia] * 0.5 + PESO_CARGA[carga] * 0.5)
    # Interações não-lineares (regras de negócio propositais)
    if veiculo == "Moto" and clima == "Tempestade/Alerta":
        score += 2.5
    if veiculo == "Caminhão" and transito == "Severo":
        score += 1.5
    if clima == "Tempestade/Alerta" and transito == "Severo":
        score += 1.0
    return score

registros = []
# Amostragem estratificada leve para cobrir o espaço de combinações + variações aleatórias
for _ in range(800):
    d = random.choice(DISTANCIAS)
    c = random.choice(CLIMAS)
    v = random.choice(VEICULOS)
    t = random.choice(TRANSITOS)
    tu = random.choice(TURNOS)
    di = random.choice(DIAS)
    ca = random.choice(CARGAS)
    s = risco(d, c, v, t, tu, di, ca)
    # threshold com uma faixa de incerteza (ruído realista, não 100% determinístico)
    prob_atraso = 1 / (1 + pow(2.71828, -(s - 4.2)))
    atraso = "Sim" if random.random() < prob_atraso else "Não"
    registros.append((d, c, v, t, tu, di, ca, atraso))

sim = [r for r in registros if r[-1] == "Sim"]
nao = [r for r in registros if r[-1] == "Não"]
random.shuffle(sim)
random.shuffle(nao)

# Monta 240 registros balanceados ~67.5% Não / 32.5% Sim (mesma proporção do relatório original, agora em dobro)
n_sim = 78
n_nao = 162
final = sim[:n_sim] + nao[:n_nao]
random.shuffle(final)

assert len(final) == 240, f"Total gerado: {len(final)}"

import os
output_csv = os.path.join(os.path.dirname(__file__), "treinamento_logistica.csv")
with open(output_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "distancia", "clima", "veiculo", "transito", "turno", "dia_semana", "tipo_carga", "atraso"])
    for i, r in enumerate(final, 1):
        w.writerow([i, *r])

print(f"Gerados {len(final)} registros | Sim: {sum(1 for r in final if r[-1]=='Sim')} | Não: {sum(1 for r in final if r[-1]=='Não')}")

