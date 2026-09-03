# Documentação do Diálogo com IA Generativa

> ⚠️ **Antes de entregar:** a atividade proíbe submeter output bruto de IA sem curadoria (Seção 5 do enunciado). Os prompts abaixo refletem o processo real de construção deste projeto — revise-os, ajuste o texto para o seu tom e, se você conversou com a IA de forma diferente em algum ponto, atualize aqui para refletir fielmente o que aconteceu. O que importa para a nota (10% do peso) é que isso seja um relato verdadeiro do seu processo, etapa por etapa — não apenas da Etapa 1.

## Prompt 1 — Modelagem do problema (Etapa 1)

**Prompt utilizado:**
"Atuando como um engenheiro de dados experiente, me ajude a modelar um problema de
classificação binária usando Naive Bayes para o domínio de Logística. Preciso definir um
rótulo alvo claro e de 6 a 8 features que influenciem esse rótulo, discretizadas em categorias
lógicas. Explique a intuição por trás dessas variáveis."

**Resposta e adoção:** a IA sugeriu o rótulo `Atraso_Na_Entrega` (Sim/Não) e propôs 7
features (Distância, Clima, Veículo, Trânsito, Turno, Dia da Semana, Tipo de Carga). O modelo
foi adotado porque reflete a operação real de logística — a IA apontou corretamente que
combinações como "Tempestade + Trânsito Severo + Moto" têm alto poder discriminativo, o
que depois se confirmou empiricamente na Etapa 4 (ver log-odds).

## Prompt 2 — Geração da massa de dados (Etapa 2)

**Prompt utilizado:**
"Gere uma lógica de pontuação de risco (em Python) que combine as 7 features definidas,
incluindo pelo menos duas regras de interação não-lineares (ex: Moto se torna
desproporcionalmente mais arriscada sob Tempestade). Use essa lógica para gerar 240
registros sintéticos, com uma margem de ruído realista (não 100% determinística), mantendo
a proporção aproximada de 65-70% 'Não' e 30-35% 'Sim'."

**Resposta e adoção:** a IA sugeriu usar um score de risco ponderado por feature, duas regras
de interação (Moto+Tempestade e Caminhão+Trânsito Severo) e uma função logística
(sigmoide) sobre o score para decidir o rótulo com uma margem de ruído, em vez de um corte
determinístico rígido — isso evita um dataset "perfeito demais", que não representaria a
variabilidade da vida real. Curadoria feita: os pesos das features e os dois limiares de
interação foram ajustados manualmente até o resultado bater com a distribuição alvo
(240 registros, 162 Não / 78 Sim), e o dataset final foi inspecionado linha a linha antes do uso.

## Prompt 3 — Código do classificador em SQL (Etapa 3)

**Prompt utilizado:**
"Escreva o classificador Naive Bayes completo em SQL (CTEs), calculando: (1) probabilidade a
priori de cada classe, (2) verossimilhança de cada feature por classe com suavização de
Laplace, (3) soma em log das probabilidades para evitar underflow, (4) normalização do score
final para uma probabilidade de 0% a 100%, e (5) uma coluna de recomendação de decisão
com base na classe de maior probabilidade."

**Resposta e adoção:** a IA gerou a estrutura em CTEs (novo_caso → estatisticas_base →
priori → verossimilhanca → score_bruto → normalização final). Curadoria feita: adicionei a
coluna `Recomendacao` (ausente na primeira versão gerada, mas exigida no enunciado — "saída
com probabilidade de cada classe **e uma recomendação de decisão**"), parametrizei o
`novo_caso` com `:parâmetros` nomeados para permitir testar múltiplos perfis sem editar o
SQL, e validei manualmente a matemática de duas linhas do resultado contra um cálculo em
Python antes de aceitar o código como correto.

## Prompt 4 — Interpretação dos testes e log-odds (Etapa 4)

**Prompt utilizado:**
"Rode o classificador para 6 perfis distintos (alto risco extremo, cenário ideal, perfil ambíguo,
dois casos isolando um único fator crítico, e um valor de veículo nunca visto no treino). Depois
calcule o log-odds de cada valor de feature entre as classes Sim/Não e aponte quais tiveram
maior poder discriminativo."

**Resposta e adoção:** os 6 casos foram executados de fato contra a base de 240 registros
(não estimados) — ver `05_Testes_e_Resultados/`. O cálculo de log-odds confirmou a intuição
da Etapa 1: `Trânsito=Severo` (log-odds 1.838) e `Clima=Tempestade/Alerta` (log-odds 1.574)
foram os fatores de maior peso a favor de "Sim", o que valida a modelagem original. Vale notar
que, com o dobro de registros, o Teste 5 (Tempestade isolada, sem trânsito severo) mudou de
classe em relação à rodada com 120 registros — sinal de que o modelo ficou mais estável com
mais dados, o que também virou material para a reflexão crítica.

