# Etapa 4 — Aplicação e Análise dos Resultados

Todos os resultados abaixo foram obtidos **executando de fato** `02_classificador_bayesiano.sql`
contra os 240 registros de `01_massa_dados.sql` (não são estimativas manuais). Ver
`resultados_brutos.json` para a saída completa das 6 execuções e `log_odds.json` para o cálculo
completo de log-odds.

## 4.1 Casos de Teste

| # | Perfil | Sim (%) | Não (%) | Classificação | Recomendação |
|---|---|---|---|---|---|
| 1 — Alto Risco Extremo | Longa, Tempestade, Moto, Severo, Noite, Dia Útil, Frágil | **98.90** | 1.10 | Sim | Acionar contingência |
| 2 — Cenário Ideal | Curta, Limpo, Caminhão, Leve, Manhã, Dia Útil, Padrão | 3.04 | **96.96** | Não | Operação padrão |
| 3 — Perfil Ambíguo | Média, Chuva Leve, Van, Moderado, Tarde, Feriado, Padrão | 10.06 | **89.94** | Não | Operação padrão |
| 4 — Fator Crítico: Trânsito | Curta, Limpo, Moto, Severo, Manhã, Dia Útil, Padrão | **54.10** | 45.90 | Sim | Acionar contingência |
| 5 — Fator Crítico: Clima | Longa, Tempestade, Caminhão, Leve, Feriado, Tarde, Padrão | 41.53 | **58.47** | Não | Operação padrão |
| 6 — Valor Não Visto (Drone) | Longa, Tempestade, **Drone**, Severo, Noite, Dia Útil, Padrão | **98.44** | 1.56 | Sim | Acionar contingência |

**Observação importante para a apresentação:** com o dobro de dados (240 vs. 120 registros), o
**Teste 5 mudou de classe** — antes "Sim" (55.43%), agora "Não" (58.47%). Isso não é um erro:
é evidência de que, com mais evidência estatística, a estimativa das verossimilhanças ficou
mais estável e o efeito isolado da "Tempestade" (sem trânsito severo, veículo robusto) não é
suficiente sozinho para inclinar a decisão. Vale citar esse ponto na apresentação — mostra que
você entende que Naive Bayes é sensível ao tamanho e à composição da amostra, não só à lógica
das features.

## 4.2 O modelo classificou conforme a intuição do domínio?

Sim, com uma ressalva relevante (ver Teste 5 acima). Os casos extremos (1 e 2) seguem
classificados com confiança muito alta (>96%) e na direção esperada. O caso ambíguo (3)
permanece menos extremo que os casos-limite, mostrando que o modelo diferencia intensidade
de risco, não só direção. Os Testes 4 e 5 isolam um único fator crítico por vez: o trânsito
severo sozinho (Teste 4) ainda empurra para "Sim", mas por margem pequena (54% vs 46%) — já a
tempestade sozinha (Teste 5), sem trânsito severo e com veículo robusto (caminhão), não é mais
suficiente para inclinar a decisão. Isso reforça que o efeito mais forte do clima aparece
combinado com outros fatores (Teste 1), não isolado.

## 4.3 Poder Discriminativo (Log-Odds) — calculado sobre os 240 registros reais

| Feature = Valor | Log-Odds (Sim vs. Não) |
|---|---|
| Trânsito = Severo | **+1.838** |
| Clima = Tempestade/Alerta | **+1.574** |
| Trânsito = Leve | −1.023 |
| Clima = Limpo | −0.812 |
| Distância = Longa | +0.651 |
| Clima = Chuva Leve | −0.564 |
| Veículo = Moto | +0.468 |
| Distância = Curta | −0.359 |

`Trânsito Severo` e `Clima = Tempestade/Alerta` continuam, com o dobro de dados, os dois
valores de maior poder discriminativo a favor de "Sim" (atraso) — os coeficientes até ficaram
mais fortes que com 120 registros (antes +1.638 e +1.473), o que é esperado: mais dados tendem
a afastar as estimativas de verossimilhança de zero, tornando os padrões mais nítidos.

## 4.4 Comportamento com Valor Não Visto (Teste 6 — "Drone")

O veículo "Drone" nunca aparece nos 240 registros de treino. Mesmo assim, o classificador
**não retornou erro nem probabilidade zerada** — devolveu 98.44% para "Sim" (ligeiramente
diferente dos 97.65% obtidos com 120 registros, porque o vocabulário e as contagens de
suavização de Laplace mudaram com a base maior). Isso ocorre graças à suavização de Laplace
(`+1` no numerador de cada verossimilhança): mesmo com contagem zero para "Drone" em ambas as
classes, a probabilidade condicional fica pequena mas positiva
(`1 / (qtd_classe + |vocabulário|)`), o que evita o underflow numérico e permite que as demais
features (Tempestade, Trânsito Severo, Longa) ainda dominem a decisão.

## 4.5 Limitações do Naive Bayes neste domínio

Ver `06_Apresentacao/reflexao_critica.md` — a limitação central é a premissa de
independência condicional entre features que, na prática, são correlacionadas (ex.: Tempestade
tende a causar Trânsito Severo), levando o modelo a "contar o mesmo risco duas vezes". A
mudança de classificação do Teste 5 entre as duas rodadas (120 → 240 registros) também expõe
uma segunda limitação prática: com poucos dados, o Naive Bayes pode ser instável para perfis
de risco intermediário — o que reforça a importância de reportar a probabilidade, não só o
rótulo binário, para decisões operacionais.

