# Resultados dos Testes e Reflexão Crítica

> **Disciplina:** Mineração de Dados  
> **Participantes:** Lucas Peres de Lima, Gabriel Lemos Gomes  
> **Entregável:** Etapa 4 do Roteiro da Atividade Prática 1  

---

## 1. Tabela Síntese dos Casos de Teste (Base com 200.000 Registros)

| # | Cenário Avaliado | P(Perda) | P(Regular) | Diagnóstico | Meta Esperada | Status |
|---|---|---|---|---|---|---|
| **1** | Baixo Risco (Planalto irrigado em outubro) | **0,18%** | **99,82%** | **Safra Regular** | P(Perda) < 5,0% | **Aprovado** |
| **2** | Alto Risco Extremo (Arenoso, seca severa, dezembro) | **98,29%** | **1,71%** | **Perda de Safra** | P(Perda) > 90,0% | **Aprovado** |
| **3** | Dilema da Irrigação (Solo arenoso sob pivô) | **3,23%** | **96,77%** | **Safra Regular** | Tecnologia compensa | **Aprovado** |
| **4** | Resiliência da Argila (Argiloso sob seca severa) | **34,65%** | **65,35%** | **Safra Regular** | Risco moderado | **Aprovado** |
| **5** | Teste de Laplace (Solo inédito fora do treino) | **22,91%** | **77,09%** | **Safra Regular** | Sem divisão por zero | **Aprovado** |

---

## 2. Respostas às Perguntas da Etapa 4

### 2.1 O modelo classificou corretamente conforme sua intuição sobre o domínio?
**Sim, com perfeita aderência agronômica.**
- No **Caso 1**, com solo argiloso, sem estiagem e com irrigação por pivô no planalto, o risco de perda foi mínimo (0,18%).
- No **Caso 2**, o acúmulo de fatores adversos (solo arenoso + seca severa + semeadura tardia em dezembro + pragas altas) resultou em probabilidade de perda de 98,29%, recomendando recusa imediata de crédito ou exigência de garantia real.
- Nos casos intermediários (Casos 3 e 4), o modelo capturou com precisão estatística o papel atenuador da tecnologia (irrigação reduziu o risco do solo arenoso para apenas 3,23%) e das propriedades físicas do solo (retenção de umidade pela microporosidade da argila manteve a safra viável em 65,35% mesmo sob seca severa).

---

### 2.2 Quais features tiveram maior log-odds (maior poder discriminativo)?

O poder discriminativo é medido pela razão de verossimilhanças na escala logarítmica:

$$\text{Log-Odds} = \ln \left( \frac{P(\text{feature} = \text{valor} \mid \text{Perda = Sim})}{P(\text{feature} = \text{valor} \mid \text{Perda = Não})} \right)$$

Quanto maior o valor absoluto ($|\text{Log-Odds}|$), maior o impacto daquela característica na decisão final.

#### Ranking das 5 categorias com maior poder separador (Base com 200.000 amostras):
1. **`seca = 'severa'` (Log-Odds = +1,3948):** É o maior impulsionador de perda da base. Estar sob seca severa multiplica a chance de perda em mais de 4 vezes em relação à safra regular ($P(\text{severa} \mid \text{Sim}) = 50,92\%$ vs $P(\text{severa} \mid \text{Não}) = 12,62\%$).
2. **`irrigacao = 'irrigado'` (Log-Odds = -1,1456):** Forte protetor de safra; contar com irrigação artificial é o maior indicador tecnológico de regularidade ($P = 13,70\%$ na regular vs apenas $4,36\%$ na perda).
3. **`seca = 'nenhuma'` (Log-Odds = -1,0529):** Ausência de estiagem é o principal indicador natural de safra dentro da meta ($P = 59,43\%$ na regular vs $20,74\%$ na perda).
4. **`tipo_solo = 'arenoso'` (Log-Odds = +0,8201):** Preditor marcante de risco de sinistro devido à baixa retenção hídrica ($P = 45,29\%$ na perda vs $19,95\%$ na regular).
5. **`chuva = 'pouca'` (Log-Odds = +0,8027):** Déficit pluviométrico geral aumenta substancialmente a vulnerabilidade ($P = 54,36\%$ na perda vs $24,36\%$ na regular).

---

### 2.3 O que acontece quando você testa um perfil com valores não vistos no treinamento?

No **Caso 5**, foi submetido um talhão com `tipo_solo = 'solo_desconhecido'`, valor que **nunca existiu nos 200.000 registros de treino**.

- **Sem a Suavização de Laplace:** A contagem de frequência seria zero ($0 / N = 0$). Na multiplicação ou na soma de logaritmos, $\ln(0) = -\infty$, o que anularia todo o cálculo e travaria o sistema com divisão por zero ou score indefinido (`NaN`).
- **Com a Suavização de Laplace Aplicada:**
  $$P(\text{solo\_desconhecido} \mid C) = \frac{0 + 1}{\text{Total}(C) + (|V_i| + 1)}$$
  O modelo expandiu dinamicamente a cardinalidade da feature ($|V_i| \leftarrow |V_i| + 1$), atribuiu uma pseudo-ocorrência $+1$ e continuou o cálculo com total estabilidade numérica, classificando o talhão com **77,09% de probabilidade de Safra Regular**, baseando-se nas outras 6 variáveis que eram favoráveis.

---

### 2.4 Quais são as limitações do Naive Bayes neste domínio específico?

A principal limitação matemática do algoritmo é a **premissa ingênua de independência condicional**:

$$P(x_1, x_2, \dots, x_7 \mid C) = \prod_{i=1}^7 P(x_i \mid C)$$

Na agronomia de campo, as variáveis **não são independentes, mas fortemente sinérgicas**:
- O impacto da estiagem (`seca = 'severa'`) é catastroficamente multiplicado se o solo for arenoso (`tipo_solo = 'arenoso'`). Na natureza, essa combinação produz um efeito não-linear desproporcional.
- Como o Naive Bayes apenas soma as evidências de forma isolada, ele não captura interações complexas de ordem superior entre atributos correlacionados, a menos que sejam criados atributos combinados explicitamente na engenharia de features.

---

## 3. Entregável 5: Reflexão Crítica

> **O que o modelo acerta, onde falha e por quê:**

O modelo Naive Bayes implementado demonstra excelência e precisão surpreendente na **triagem de grandes carteiras agrícolas**, operando em alta velocidade e com explicabilidade transparente de cada pontuação logarítmica. Ele **acerta com grande consistência** os casos extremos de baixo risco (fazendas estruturadas, irrigadas e no planalto) e de alto risco (solos arenosos com estiagem e pragas), permitindo a automatização confiável da liberação de crédito rural e emissão de apólices de seguro.

Entretanto, o modelo **falha na calibração fina de cenários agronômicos com compensação tecnológica complexa**. Devido à premissa de independência condicional, o algoritmo penaliza um talhão pela ocorrência de pouca chuva mesmo quando ele possui pivô central de irrigação pleno, pois avalia o atributo "chuva" de forma isolada da "irrigação". Na prática agrícola, a presença do pivô anula completamente o déficit de chuva. Portanto, o Naive Bayes deve ser utilizado como um **sistema inteligente de triagem inicial de risco**, devendo os casos limítrofes (com probabilidades entre 40% e 60%) ser encaminhados para análise agronômica individual ou modelos com árvores de decisão.
