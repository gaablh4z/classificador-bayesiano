"""
Gerador da massa de dados de treinamento - Classificador Bayesiano de Atrasos em Entregas
Domínio: Logística
Gera 240 registros com padrões de risco INTENCIONAIS (não puramente aleatórios),
combinando pesos por feature + regras de interação (ex: Moto + Tempestade agrava o risco).
"""
# ==============================================================================
# 1. IMPORTAÇÃO DE BIBLIOTECAS
# ==============================================================================
# Importa módulos para:
# - random: sorteios e números aleatórios
# - csv: criação e escrita do arquivo de dados estruturado (.csv)
# - os: manipulação de diretórios e caminhos de arquivos
import random
import csv
import os

# ==============================================================================
# 2. DEFINIÇÃO DA SEMENTE ALEATÓRIA (SEED)
# ==============================================================================
# Fixa a semente do gerador de números aleatórios.
# Isso garante que a geração seja reproduzível (gera exatamente os mesmos dados sempre).
random.seed(42)

# ==============================================================================
# 3. DOMÍNIOS E VALORES POSSÍVEIS DAS FEATURES (ATRIBUTOS)
# ==============================================================================
# Lista todos os valores possíveis para cada característica de uma entrega.
DISTANCIAS = ["Curta", "Média", "Longa"]
CLIMAS = ["Limpo", "Chuva Leve", "Tempestade/Alerta"]
VEICULOS = ["Moto", "Van", "Caminhão"]
TRANSITOS = ["Leve", "Moderado", "Severo"]
TURNOS = ["Manhã", "Tarde", "Noite"]
DIAS = ["Dia Útil", "Final de Semana/Feriado"]
CARGAS = ["Padrão", "Frágil/Volume Especial"]

# ==============================================================================
# 4. TABELAS DE PESOS DE RISCO INDIVIDUAL
# ==============================================================================
# Define o peso de risco de cada valor.
# Cenários desfavoráveis recebem notas maiores (ex: Tempestade = 3, Trânsito Severo = 3).
PESO_DIST = {"Curta": 0, "Média": 1, "Longa": 2}
PESO_CLIMA = {"Limpo": 0, "Chuva Leve": 1, "Tempestade/Alerta": 3}
PESO_VEIC = {"Caminhão": 0, "Van": 1, "Moto": 2}
PESO_TRANS = {"Leve": 0, "Moderado": 1, "Severo": 3}
PESO_TURNO = {"Manhã": 0, "Tarde": 0, "Noite": 1}
PESO_DIA = {"Dia Útil": 1, "Final de Semana/Feriado": 0}
PESO_CARGA = {"Padrão": 0, "Frágil/Volume Especial": 1}

# ==============================================================================
# 5. FUNÇÃO DE CÁLCULO DO SCORE DE RISCO
# ==============================================================================
# Calcula a pontuação total de risco de uma entrega:
# - Soma o peso base de cada uma das características;
# - Aplica penalidades extras para combinações críticas da vida real
#   (exemplo: Moto em Tempestade ou Caminhão em Trânsito Severo).
def risco(distancia, clima, veiculo, transito, turno, dia, carga):
    score = (PESO_DIST[distancia] + PESO_CLIMA[clima] + PESO_VEIC[veiculo] +
             PESO_TRANS[transito] + PESO_TURNO[turno] * 0.5 +
             PESO_DIA[dia] * 0.5 + PESO_CARGA[carga] * 0.5)
    
    # Regras de interação (agravantes combinados)
    if veiculo == "Moto" and clima == "Tempestade/Alerta":
        score += 2.5
    if veiculo == "Caminhão" and transito == "Severo":
        score += 1.5
    if clima == "Tempestade/Alerta" and transito == "Severo":
        score += 1.0
    return score

# ==============================================================================
# 6. GERAÇÃO DE AMOSTRAS E CÁLCULO PROBABILÍSTICO DE ATRASO
# ==============================================================================
# Sorteia 800 combinações possíveis de entregas.
# Converte o score de risco em probabilidade usando uma função logística (sigmoide)
# e define de forma probabilística se a entrega atrasou ("Sim") ou não ("Não").
registros = []
for _ in range(800):
    d = random.choice(DISTANCIAS)
    c = random.choice(CLIMAS)
    v = random.choice(VEICULOS)
    t = random.choice(TRANSITOS)
    tu = random.choice(TURNOS)
    di = random.choice(DIAS)
    ca = random.choice(CARGAS)
    s = risco(d, c, v, t, tu, di, ca)
    
    # Função logística: transforma a pontuação em chance entre 0% e 100%
    prob_atraso = 1 / (1 + pow(2.71828, -(s - 4.2)))
    atraso = "Sim" if random.random() < prob_atraso else "Não"
    registros.append((d, c, v, t, tu, di, ca, atraso))

# ==============================================================================
# 7. SEPARAÇÃO E BALANCEAMENTO DAS CLASSES
# ==============================================================================
# Separa os registros gerados entre os que atrasaram e os que chegaram no prazo,
# embaralhando as listas para garantir variedade.
sim = [r for r in registros if r[-1] == "Sim"]
nao = [r for r in registros if r[-1] == "Não"]
random.shuffle(sim)
random.shuffle(nao)

# ==============================================================================
# 8. MONTAGEM DA MASSA FINAL (240 REGISTROS)
# ==============================================================================
# Seleciona exatamente a proporção desejada de registros:
# - 162 registros "Não" (67.5% - pontualidade usual)
# - 78 registros "Sim" (32.5% - taxa real de atraso)
# Em seguida, mistura todos os registros.
n_sim = 78
n_nao = 162
final = sim[:n_sim] + nao[:n_nao]
random.shuffle(final)

# Garante que o total gerado é exatamente 240
assert len(final) == 240, f"Total gerado: {len(final)}"

# ==============================================================================
# 9. SALVAMENTO DOS DADOS NO ARQUIVO CSV
# ==============================================================================
# Cria o arquivo 'treinamento_logistica.csv' na mesma pasta deste script,
# escreve a linha de cabeçalho e insere todas as 240 linhas numeradas por ID.
output_csv = os.path.join(os.path.dirname(__file__), "treinamento_logistica.csv")
with open(output_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "distancia", "clima", "veiculo", "transito", "turno", "dia_semana", "tipo_carga", "atraso"])
    for i, r in enumerate(final, 1):
        w.writerow([i, *r])

# ==============================================================================
# 10. EXIBIÇÃO DO RESUMO FINAL
# ==============================================================================
# Mostra no console o total de registros salvos e a divisão entre atrasos e não atrasos.
print(f"Gerados {len(final)} registros | Sim: {sum(1 for r in final if r[-1]=='Sim')} | Não: {sum(1 for r in final if r[-1]=='Não')}")


