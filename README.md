# Classificador Naive Bayes para Previsão de Quebra de Safra Agrícola

Projeto prático desenvolvido para a disciplina de **Mineração de Dados** (Engenharia de Computação). O objetivo é construir e avaliar um **Classificador Naive Bayes** implementado em **SQL puro** (SQLite) e orquestrado em **Python**, voltado para a previsão de risco de **quebra de safra** e acionamento de seguro agrícola em talhões produtivos do Centro-Oeste brasileiro (com calibração baseada em parâmetros edafoclimáticos do Mato Grosso).

---

## 🌾 Contexto do Problema

O agronegócio de grãos opera sob forte influência de fatores climáticos e edáficos (solo). Seguradoras e instituições financeiras (PROAGRO e crédito rural) precisam avaliar o risco de sinistro agrícola com antecedência para precificação de prêmios e liberação de custeio.

- **Rótulo Alvo (`perda_safra`):**
  - `'sim'`: Quebra de safra (queda de produtividade $> 30\%$ em relação à média histórica regional — aciona seguro).
  - `'nao'`: Safra regular (produtividade dentro da meta econômica regional $\ge 70\%$).

---

## 📊 Features e Discretização (ZARC / Embrapa)

Foram selecionadas 7 variáveis agronômicas fundamentais, discretizadas em 3 categorias cada ($|V_i| = 3$):

| Feature | Descrição | Categorias |
|---|---|---|
| `tipo_solo` | Textura e retenção hídrica | `argiloso`, `medio`, `arenoso` |
| `seca` | Período de estiagem em fases críticas | `nenhuma`, `moderada`, `severa` |
| `chuva` | Volume pluviométrico acumulado no ciclo | `normal`, `excessiva`, `pouca` |
| `mes_plantio` | Janela de semeadura (ZARC) | `outubro`, `novembro`, `dezembro` |
| `irrigacao` | Manejo hídrico e cobertura | `plantio_direto`, `convencional`, `irrigado` |
| `pragas` | Pressão fitossanitária | `baixa`, `media`, `alta` |
| `regiao` | Macroambiente e altitude | `planalto`, `transicao`, `baixada` |

---

## 🧮 Formulação Matemática do Classificador

1. **Probabilidades a Priori:**
   $$P(C) = \frac{\text{Total}(C)}{N}$$

2. **Verossimilhança com Suavização de Laplace:**
   $$P(x_i \mid C) = \frac{\text{Contagem}(x_i \text{ em } C) + 1}{\text{Total}(C) + |V_i|}$$

3. **Soma em Log-Probabilidades (Anti-Underflow):**
   $$\text{Score}(C) = \ln(P(C)) + \sum_{i=1}^7 \ln(P(x_i \mid C))$$

4. **Normalização por Softmax Estável:**
   $$P(\text{sim}) = \frac{e^{\text{Score}(\text{sim}) - \text{max}}}{e^{\text{Score}(\text{sim}) - \text{max}} + e^{\text{Score}(\text{nao}) - \text{max}}} \times 100\%$$

---

## 📁 Estrutura do Repositório

```
.
├── 01_Prompts/
│   └── prompts_documentados.md         # Registro integral de prompts e diálogo com a IA
├── 02_Modelagem/
│   └── relatorio_modelagem.md          # Relatório técnico completo de modelagem
├── 03_Dataset/
│   ├── gerar_dataset.py                # Script gerador de massa de dados sintética (200k registros)
│   ├── safra_treinamento.csv           # Base de dados em CSV
│   ├── safra_treinamento.sql           # Script de inserção em SQL
│   └── safra_treinamento.db            # Banco de dados SQLite gerado
├── 04_Codigo_SQL/
│   ├── 01_massa_dados.sql              # DDL e carga dos dados
│   ├── 02_classificador_bayesiano.sql  # Implementação do Naive Bayes em SQL puro
│   └── executar_testes.py              # Script executor dos casos de teste
├── 05_Testes_e_Resultados/
│   ├── casos_teste.csv                 # 5 perfis de talhões testados
│   ├── log_odds.json                   # Cálculo de log-odds para análise de impacto
│   ├── resultados_brutos.json          # Probabilidades calculadas por cenário
│   └── resultados_e_analise.md         # Relatório analítico dos resultados e reflexão crítica
```

---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.8+
- SQLite 3

### 1. (Opcional) Gerar novamente a massa de dados
```bash
python 03_Dataset/gerar_dataset.py
```

### 2. Executar o Classificador e Validar os Casos de Teste
```bash
python 04_Codigo_SQL/executar_testes.py
```

Os resultados consolidados e os relatórios serão atualizados na pasta `05_Testes_e_Resultados/`.

---

## 📈 Resumo dos Resultados

| # | Cenário Avaliado | P(Perda) | P(Regular) | Diagnóstico | Meta Esperada | Status |
|---|---|---|---|---|---|---|
| **1** | Baixo Risco (Planalto irrigado em outubro) | **0,18%** | **99,82%** | Safra Regular | P(Perda) < 5,0% | Aprovado |
| **2** | Alto Risco Extremo (Arenoso, seca severa, dezembro) | **98,29%** | **1,71%** | Perda de Safra | P(Perda) > 90,0% | Aprovado |
| **3** | Dilema da Irrigação (Solo arenoso sob pivô) | **3,23%** | **96,77%** | Safra Regular | Tecnologia compensa | Aprovado |
| **4** | Resiliência da Argila (Argiloso sob seca severa) | **34,65%** | **65,35%** | Safra Regular | Risco moderado | Aprovado |
| **5** | Teste de Laplace (Solo inédito fora do treino) | **22,91%** | **77,09%** | Safra Regular | Sem divisão por zero | Aprovado |

---

## 👥 Participantes

- **Lucas Peres de Lima**
- **Gabriel Lemos Gomes** ([@gaablh4z](https://github.com/gaablh4z))
