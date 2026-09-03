# Contexto para o Antigravity CLI — Atividade Prática 1 (Classificador Bayesiano)

Instrução para o agente: crie/sobrescreva exatamente os arquivos abaixo, nos caminhos indicados,
dentro da pasta raiz do projeto "Classificador B..." já existente no VS Code (que já tem as pastas
01_Prompts, 02_Modelagem, 03_Dataset, 04_Codigo_SQL, 05_Testes_e_Resultados, 06_Apresentacao,
Atividade/ e README.md). Preserve os .gitkeep. Não altere Atividade/Atividade.pdf (é o enunciado).

A base de dados usa 240 registros de treinamento (162 'Não' / 78 'Sim', proporção 67.5%/32.5%).
Depois de criar os arquivos, rode `python3 03_Dataset/gerar_dataset.py` para regenerar o CSV (ou
apenas use o CSV já embutido abaixo), e valide o SQL do classificador rodando os 6 casos de teste
descritos em 05_Testes_e_Resultados/resultados_e_analise.md contra um SQLite/DuckDB local antes de
considerar a tarefa concluída.

IMPORTANTE: o arquivo 02_Modelagem/relatorio_modelagem.md tem um campo "Nome do(s) aluno(s)" com
placeholder — pergunte ao usuário o nome real antes de finalizar, ou deixe marcado para preenchimento manual.


---

## Arquivo: `01_Prompts/prompts_documentados.md`

```md
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

```


---

## Arquivo: `02_Modelagem/relatorio_modelagem.md`

```md
# Relatório de Modelagem — Classificador Bayesiano de Atrasos em Entregas

**Nome do(s) aluno(s):** ⚠️ *preencher — o PDF original ainda está com o placeholder "[Preencha seu Nome]", isso reprova por si só se for entregue assim*
**Disciplina/Curso:** Engenharia da Computação
**Data de entrega:** 28/08/2026

## 1.1 Domínio e Problema Escolhido

Domínio: **Logística**. Problema: prever proativamente se uma entrega sofrerá atraso,
permitindo alocação dinâmica de recursos (ex.: troca de modal de transporte) antes que a
falha ocorra na ponta.

## 1.2 Rótulo Alvo

`Atraso_Na_Entrega`:
- **Sim** — a entrega ocorrerá fora do prazo estipulado (SLA quebrado).
- **Não** — a entrega será realizada no prazo normal.

## 1.3 Features Relevantes e Discretização

| Feature | Lógica / Motivação | Categorias |
|---|---|---|
| Distância da Rota | Rotas mais longas têm maior exposição a eventos imprevistos. | Curta, Média, Longa |
| Condição Climática | Chuva/tempestade reduzem velocidade e aumentam acidentes. | Limpo, Chuva Leve, Tempestade/Alerta |
| Tipo de Veículo | Motos são mais vulneráveis ao clima; caminhões são mais afetados pelo trânsito. | Moto, Van, Caminhão |
| Trânsito na Rota | Congestionamento é causa direta de perda de tempo. | Leve, Moderado, Severo |
| Turno de Despacho | Noite tem menor visibilidade, porém menos tráfego. | Manhã, Tarde, Noite |
| Dia da Semana | Dias úteis concentram maior densidade urbana comercial. | Dia Útil, Final de Semana/Feriado |
| Tipo de Carga | Cargas frágeis exigem direção defensiva, reduzindo velocidade média. | Padrão, Frágil/Volume Especial |

## 1.4 Lógica Intuitiva dos Padrões

A probabilidade de atraso aumenta quando fatores de risco se combinam — ex.: "Tempestade"
agrava o risco de forma desproporcional se o veículo for uma "Moto". Já um "Caminhão" em
rota "Curta", clima "Limpo" e trânsito "Leve" tem risco marginal. O Naive Bayes mede a
probabilidade condicional de cada fator dado o resultado (ex.: "qual a chance de estar
chovendo DADO que a entrega atrasou?") e multiplica esses fatores assumindo independência
entre eles — essa é justamente a premissa "ingênua" discutida na reflexão crítica (Etapa 5).

## 1.5 Diálogo com a IA Generativa

Ver `01_Prompts/prompts_documentados.md` para o histórico completo (Prompts 1 a 4, cobrindo
modelagem, geração de dados, código SQL e interpretação dos testes — o relatório original
só documentava o Prompt 1, o que fica abaixo do exigido no enunciado).

```


---

## Arquivo: `03_Dataset/treinamento_logistica.csv`

```csv
id,distancia,clima,veiculo,transito,turno,dia_semana,tipo_carga,atraso
1,Curta,Chuva Leve,Caminhão,Leve,Noite,Final de Semana/Feriado,Frágil/Volume Especial,Não
2,Longa,Limpo,Van,Moderado,Manhã,Dia Útil,Padrão,Sim
3,Longa,Tempestade/Alerta,Van,Leve,Noite,Dia Útil,Frágil/Volume Especial,Não
4,Longa,Limpo,Caminhão,Moderado,Noite,Dia Útil,Frágil/Volume Especial,Não
5,Curta,Tempestade/Alerta,Caminhão,Severo,Tarde,Final de Semana/Feriado,Frágil/Volume Especial,Sim
6,Média,Chuva Leve,Van,Moderado,Tarde,Dia Útil,Padrão,Não
7,Longa,Limpo,Caminhão,Leve,Noite,Final de Semana/Feriado,Padrão,Não
8,Curta,Limpo,Caminhão,Leve,Manhã,Dia Útil,Padrão,Não
9,Longa,Tempestade/Alerta,Van,Severo,Noite,Dia Útil,Padrão,Sim
10,Média,Limpo,Van,Moderado,Tarde,Final de Semana/Feriado,Frágil/Volume Especial,Não
11,Curta,Limpo,Moto,Severo,Tarde,Final de Semana/Feriado,Padrão,Não
12,Longa,Limpo,Van,Leve,Manhã,Dia Útil,Padrão,Não
13,Média,Limpo,Moto,Moderado,Manhã,Final de Semana/Feriado,Frágil/Volume Especial,Não
14,Curta,Limpo,Caminhão,Moderado,Manhã,Dia Útil,Padrão,Não
15,Longa,Tempestade/Alerta,Moto,Severo,Noite,Final de Semana/Feriado,Frágil/Volume Especial,Sim
16,Média,Tempestade/Alerta,Van,Severo,Tarde,Final de Semana/Feriado,Frágil/Volume Especial,Sim
17,Média,Chuva Leve,Moto,Leve,Noite,Dia Útil,Frágil/Volume Especial,Não
18,Média,Limpo,Caminhão,Leve,Noite,Final de Semana/Feriado,Padrão,Não
19,Média,Limpo,Caminhão,Severo,Manhã,Dia Útil,Frágil/Volume Especial,Sim
20,Média,Chuva Leve,Moto,Leve,Manhã,Dia Útil,Frágil/Volume Especial,Não
21,Média,Chuva Leve,Moto,Leve,Manhã,Final de Semana/Feriado,Padrão,Não
22,Curta,Tempestade/Alerta,Van,Severo,Tarde,Final de Semana/Feriado,Padrão,Sim
23,Média,Limpo,Van,Leve,Noite,Final de Semana/Feriado,Frágil/Volume Especial,Não
24,Média,Limpo,Caminhão,Moderado,Noite,Final de Semana/Feriado,Padrão,Não
25,Média,Tempestade/Alerta,Caminhão,Moderado,Noite,Dia Útil,Padrão,Sim
26,Curta,Tempestade/Alerta,Caminhão,Leve,Tarde,Dia Útil,Padrão,Não
27,Longa,Limpo,Caminhão,Moderado,Manhã,Dia Útil,Frágil/Volume Especial,Não
28,Curta,Chuva Leve,Van,Severo,Manhã,Final de Semana/Feriado,Padrão,Não
29,Média,Limpo,Caminhão,Moderado,Tarde,Final de Semana/Feriado,Frágil/Volume Especial,Não
30,Longa,Limpo,Caminhão,Moderado,Manhã,Dia Útil,Padrão,Não
31,Média,Tempestade/Alerta,Van,Moderado,Noite,Final de Semana/Feriado,Padrão,Sim
32,Média,Chuva Leve,Moto,Leve,Tarde,Final de Semana/Feriado,Padrão,Não
33,Média,Limpo,Caminhão,Leve,Manhã,Final de Semana/Feriado,Padrão,Não
34,Média,Limpo,Moto,Moderado,Manhã,Dia Útil,Frágil/Volume Especial,Não
35,Curta,Tempestade/Alerta,Caminhão,Leve,Noite,Final de Semana/Feriado,Frágil/Volume Especial,Sim
36,Longa,Chuva Leve,Caminhão,Leve,Tarde,Final de Semana/Feriado,Padrão,Não
37,Curta,Chuva Leve,Caminhão,Leve,Noite,Dia Útil,Padrão,Não
38,Longa,Tempestade/Alerta,Caminhão,Moderado,Manhã,Dia Útil,Frágil/Volume Especial,Sim
39,Longa,Limpo,Van,Leve,Noite,Final de Semana/Feriado,Frágil/Volume Especial,Não
40,Média,Limpo,Moto,Moderado,Tarde,Dia Útil,Padrão,Não
41,Média,Chuva Leve,Moto,Leve,Tarde,Final de Semana/Feriado,Padrão,Não
42,Curta,Limpo,Van,Leve,Tarde,Final de Semana/Feriado,Padrão,Não
43,Longa,Chuva Leve,Van,Moderado,Noite,Final de Semana/Feriado,Frágil/Volume Especial,Sim
44,Média,Chuva Leve,Caminhão,Leve,Noite,Dia Útil,Padrão,Não
45,Média,Tempestade/Alerta,Caminhão,Severo,Manhã,Dia Útil,Padrão,Sim
46,Média,Chuva Leve,Moto,Leve,Tarde,Final de Semana/Feriado,Padrão,Não
47,Curta,Limpo,Moto,Moderado,Manhã,Final de Semana/Feriado,Padrão,Não
48,Curta,Limpo,Van,Leve,Manhã,Dia Útil,Frágil/Volume Especial,Não
49,Longa,Limpo,Moto,Severo,Tarde,Dia Útil,Padrão,Sim
50,Curta,Limpo,Van,Moderado,Noite,Final de Semana/Feriado,Frágil/Volume Especial,Não
51,Média,Limpo,Van,Moderado,Noite,Final de Semana/Feriado,Frágil/Volume Especial,Sim
52,Média,Chuva Leve,Van,Moderado,Tarde,Final de Semana/Feriado,Padrão,Não
53,Curta,Chuva Leve,Van,Moderado,Tarde,Final de Semana/Feriado,Frágil/Volume Especial,Não
54,Longa,Limpo,Caminhão,Leve,Manhã,Dia Útil,Frágil/Volume Especial,Não
55,Curta,Chuva Leve,Van,Moderado,Noite,Final de Semana/Feriado,Frágil/Volume Especial,Não
56,Curta,Chuva Leve,Van,Leve,Tarde,Dia Útil,Frágil/Volume Especial,Não
57,Curta,Chuva Leve,Moto,Moderado,Manhã,Final de Semana/Feriado,Padrão,Não
58,Média,Tempestade/Alerta,Van,Severo,Manhã,Dia Útil,Frágil/Volume Especial,Sim
59,Média,Chuva Leve,Van,Severo,Tarde,Final de Semana/Feriado,Frágil/Volume Especial,Não
60,Curta,Chuva Leve,Caminhão,Moderado,Noite,Final de Semana/Feriado,Padrão,Não
61,Curta,Tempestade/Alerta,Van,Severo,Tarde,Dia Útil,Frágil/Volume Especial,Sim
62,Curta,Chuva Leve,Moto,Moderado,Manhã,Final de Semana/Feriado,Padrão,Não
63,Média,Chuva Leve,Moto,Moderado,Tarde,Dia Útil,Frágil/Volume Especial,Sim
64,Média,Limpo,Van,Moderado,Manhã,Final de Semana/Feriado,Padrão,Não
65,Curta,Chuva Leve,Van,Leve,Tarde,Final de Semana/Feriado,Frágil/Volume Especial,Não
66,Média,Limpo,Caminhão,Moderado,Noite,Dia Útil,Padrão,Não
67,Curta,Tempestade/Alerta,Caminhão,Severo,Manhã,Dia Útil,Padrão,Sim
68,Média,Limpo,Moto,Moderado,Tarde,Dia Útil,Frágil/Volume Especial,Não
69,Curta,Chuva Leve,Van,Severo,Tarde,Final de Semana/Feriado,Padrão,Sim
70,Média,Limpo,Moto,Leve,Manhã,Dia Útil,Frágil/Volume Especial,Não
71,Curta,Limpo,Caminhão,Leve,Tarde,Final de Semana/Feriado,Padrão,Não
72,Curta,Tempestade/Alerta,Caminhão,Severo,Noite,Dia Útil,Frágil/Volume Especial,Sim
73,Média,Tempestade/Alerta,Moto,Leve,Tarde,Final de Semana/Feriado,Frágil/Volume Especial,Sim
74,Curta,Chuva Leve,Moto,Moderado,Manhã,Dia Útil,Frágil/Volume Especial,Não
75,Curta,Chuva Leve,Moto,Moderado,Noite,Final de Semana/Feriado,Padrão,Sim
76,Longa,Chuva Leve,Caminhão,Severo,Tarde,Dia Útil,Frágil/Volume Especial,Sim
77,Média,Chuva Leve,Van,Moderado,Manhã,Final de Semana/Feriado,Padrão,Não
78,Longa,Chuva Leve,Caminhão,Leve,Noite,Dia Útil,Frágil/Volume Especial,Não
79,Média,Limpo,Caminhão,Leve,Noite,Final de Semana/Feriado,Padrão,Não
80,Média,Limpo,Caminhão,Moderado,Manhã,Dia Útil,Frágil/Volume Especial,Não
81,Média,Chuva Leve,Caminhão,Leve,Tarde,Final de Semana/Feriado,Padrão,Não
82,Média,Chuva Leve,Moto,Severo,Tarde,Final de Semana/Feriado,Padrão,Sim
83,Longa,Tempestade/Alerta,Moto,Moderado,Tarde,Final de Semana/Feriado,Frágil/Volume Especial,Sim
84,Média,Limpo,Van,Leve,Noite,Dia Útil,Frágil/Volume Especial,Não
85,Longa,Tempestade/Alerta,Van,Moderado,Noite,Final de Semana/Feriado,Padrão,Sim
86,Longa,Chuva Leve,Moto,Leve,Noite,Dia Útil,Padrão,Não
87,Média,Tempestade/Alerta,Caminhão,Moderado,Manhã,Dia Útil,Padrão,Não
88,Curta,Limpo,Caminhão,Moderado,Manhã,Final de Semana/Feriado,Padrão,Não
89,Curta,Limpo,Van,Leve,Noite,Final de Semana/Feriado,Padrão,Não
90,Curta,Chuva Leve,Moto,Leve,Manhã,Final de Semana/Feriado,Frágil/Volume Especial,Não
91,Longa,Tempestade/Alerta,Van,Moderado,Manhã,Final de Semana/Feriado,Padrão,Sim
92,Longa,Chuva Leve,Moto,Severo,Noite,Final de Semana/Feriado,Frágil/Volume Especial,Sim
93,Curta,Chuva Leve,Moto,Severo,Noite,Dia Útil,Padrão,Sim
94,Média,Chuva Leve,Caminhão,Moderado,Manhã,Final de Semana/Feriado,Padrão,Não
95,Curta,Tempestade/Alerta,Caminhão,Leve,Noite,Final de Semana/Feriado,Frágil/Volume Especial,Sim
96,Curta,Chuva Leve,Caminhão,Moderado,Tarde,Dia Útil,Padrão,Não
97,Longa,Chuva Leve,Caminhão,Severo,Tarde,Dia Útil,Frágil/Volume Especial,Sim
98,Longa,Limpo,Van,Moderado,Noite,Final de Semana/Feriado,Padrão,Sim
99,Curta,Chuva Leve,Caminhão,Leve,Noite,Dia Útil,Frágil/Volume Especial,Não
100,Longa,Tempestade/Alerta,Moto,Severo,Manhã,Final de Semana/Feriado,Padrão,Sim
101,Longa,Tempestade/Alerta,Moto,Leve,Noite,Final de Semana/Feriado,Frágil/Volume Especial,Sim
102,Média,Limpo,Caminhão,Moderado,Tarde,Dia Útil,Frágil/Volume Especial,Não
103,Longa,Limpo,Caminhão,Moderado,Tarde,Dia Útil,Frágil/Volume Especial,Não
104,Média,Limpo,Van,Leve,Noite,Dia Útil,Padrão,Não
105,Média,Tempestade/Alerta,Caminhão,Moderado,Noite,Dia Útil,Frágil/Volume Especial,Sim
106,Curta,Tempestade/Alerta,Caminhão,Moderado,Tarde,Final de Semana/Feriado,Padrão,Não
107,Curta,Tempestade/Alerta,Moto,Moderado,Tarde,Dia Útil,Frágil/Volume Especial,Sim
108,Média,Limpo,Moto,Moderado,Manhã,Dia Útil,Frágil/Volume Especial,Sim
109,Curta,Tempestade/Alerta,Moto,Severo,Manhã,Final de Semana/Feriado,Padrão,Sim
110,Curta,Limpo,Van,Moderado,Tarde,Final de Semana/Feriado,Frágil/Volume Especial,Não
111,Longa,Limpo,Caminhão,Moderado,Tarde,Final de Semana/Feriado,Padrão,Não
112,Curta,Chuva Leve,Van,Leve,Noite,Dia Útil,Padrão,Não
113,Curta,Chuva Leve,Caminhão,Leve,Manhã,Final de Semana/Feriado,Padrão,Não
114,Média,Limpo,Caminhão,Moderado,Tarde,Dia Útil,Frágil/Volume Especial,Não
115,Longa,Limpo,Caminhão,Moderado,Noite,Final de Semana/Feriado,Frágil/Volume Especial,Sim
116,Média,Chuva Leve,Moto,Moderado,Tarde,Final de Semana/Feriado,Padrão,Não
117,Longa,Tempestade/Alerta,Moto,Leve,Tarde,Dia Útil,Padrão,Sim
118,Longa,Limpo,Moto,Leve,Tarde,Dia Útil,Padrão,Não
119,Longa,Chuva Leve,Moto,Severo,Manhã,Final de Semana/Feriado,Frágil/Volume Especial,Sim
120,Média,Limpo,Moto,Leve,Tarde,Final de Semana/Feriado,Padrão,Não
121,Média,Chuva Leve,Caminhão,Severo,Manhã,Dia Útil,Frágil/Volume Especial,Sim
122,Curta,Tempestade/Alerta,Van,Leve,Manhã,Dia Útil,Padrão,Não
123,Longa,Chuva Leve,Caminhão,Moderado,Noite,Final de Semana/Feriado,Padrão,Não
124,Curta,Limpo,Moto,Moderado,Tarde,Dia Útil,Frágil/Volume Especial,Não
125,Média,Limpo,Moto,Moderado,Manhã,Final de Semana/Feriado,Frágil/Volume Especial,Não
126,Média,Limpo,Van,Moderado,Noite,Final de Semana/Feriado,Padrão,Não
127,Longa,Limpo,Moto,Moderado,Tarde,Final de Semana/Feriado,Frágil/Volume Especial,Sim
128,Curta,Chuva Leve,Caminhão,Leve,Manhã,Dia Útil,Padrão,Não
129,Curta,Limpo,Moto,Leve,Manhã,Final de Semana/Feriado,Padrão,Não
130,Média,Chuva Leve,Caminhão,Leve,Tarde,Final de Semana/Feriado,Padrão,Não
131,Longa,Limpo,Moto,Moderado,Noite,Dia Útil,Padrão,Sim
132,Média,Limpo,Van,Moderado,Tarde,Final de Semana/Feriado,Padrão,Não
133,Média,Chuva Leve,Moto,Severo,Noite,Dia Útil,Frágil/Volume Especial,Sim
134,Curta,Limpo,Van,Leve,Tarde,Dia Útil,Frágil/Volume Especial,Não
135,Longa,Chuva Leve,Caminhão,Moderado,Manhã,Dia Útil,Frágil/Volume Especial,Não
136,Longa,Limpo,Van,Moderado,Noite,Final de Semana/Feriado,Frágil/Volume Especial,Não
137,Curta,Tempestade/Alerta,Caminhão,Leve,Tarde,Final de Semana/Feriado,Padrão,Não
138,Média,Chuva Leve,Caminhão,Moderado,Manhã,Final de Semana/Feriado,Padrão,Não
139,Curta,Chuva Leve,Caminhão,Leve,Manhã,Final de Semana/Feriado,Frágil/Volume Especial,Não
140,Curta,Limpo,Moto,Leve,Noite,Final de Semana/Feriado,Frágil/Volume Especial,Não
141,Curta,Limpo,Van,Moderado,Manhã,Final de Semana/Feriado,Padrão,Sim
142,Curta,Chuva Leve,Moto,Moderado,Noite,Dia Útil,Frágil/Volume Especial,Não
143,Curta,Tempestade/Alerta,Caminhão,Moderado,Manhã,Dia Útil,Frágil/Volume Especial,Não
144,Média,Limpo,Moto,Moderado,Noite,Dia Útil,Padrão,Não
145,Média,Limpo,Caminhão,Moderado,Manhã,Dia Útil,Frágil/Volume Especial,Não
146,Média,Tempestade/Alerta,Moto,Severo,Noite,Dia Útil,Padrão,Sim
147,Curta,Chuva Leve,Caminhão,Leve,Noite,Dia Útil,Padrão,Não
148,Média,Chuva Leve,Van,Leve,Manhã,Final de Semana/Feriado,Frágil/Volume Especial,Não
149,Longa,Limpo,Caminhão,Severo,Tarde,Final de Semana/Feriado,Frágil/Volume Especial,Sim
150,Média,Limpo,Van,Leve,Noite,Final de Semana/Feriado,Padrão,Não
151,Longa,Chuva Leve,Van,Moderado,Tarde,Dia Útil,Padrão,Não
152,Curta,Limpo,Van,Severo,Tarde,Final de Semana/Feriado,Frágil/Volume Especial,Não
153,Longa,Tempestade/Alerta,Caminhão,Moderado,Noite,Final de Semana/Feriado,Frágil/Volume Especial,Não
154,Longa,Limpo,Caminhão,Leve,Tarde,Dia Útil,Padrão,Não
155,Longa,Tempestade/Alerta,Caminhão,Leve,Tarde,Dia Útil,Frágil/Volume Especial,Sim
156,Média,Tempestade/Alerta,Van,Severo,Tarde,Dia Útil,Padrão,Sim
157,Média,Limpo,Van,Leve,Manhã,Final de Semana/Feriado,Padrão,Não
158,Curta,Tempestade/Alerta,Moto,Severo,Manhã,Dia Útil,Padrão,Sim
159,Longa,Tempestade/Alerta,Moto,Severo,Tarde,Final de Semana/Feriado,Padrão,Sim
160,Curta,Chuva Leve,Caminhão,Severo,Tarde,Final de Semana/Feriado,Padrão,Não
161,Curta,Chuva Leve,Caminhão,Moderado,Tarde,Final de Semana/Feriado,Padrão,Não
162,Curta,Tempestade/Alerta,Caminhão,Leve,Manhã,Dia Útil,Padrão,Sim
163,Média,Chuva Leve,Caminhão,Moderado,Tarde,Dia Útil,Padrão,Não
164,Curta,Chuva Leve,Caminhão,Leve,Tarde,Dia Útil,Frágil/Volume Especial,Não
165,Curta,Tempestade/Alerta,Caminhão,Moderado,Manhã,Dia Útil,Frágil/Volume Especial,Não
166,Média,Tempestade/Alerta,Caminhão,Moderado,Manhã,Dia Útil,Frágil/Volume Especial,Não
167,Curta,Tempestade/Alerta,Van,Moderado,Manhã,Dia Útil,Frágil/Volume Especial,Sim
168,Curta,Chuva Leve,Van,Leve,Tarde,Dia Útil,Frágil/Volume Especial,Não
169,Curta,Limpo,Moto,Leve,Manhã,Final de Semana/Feriado,Padrão,Não
170,Média,Tempestade/Alerta,Caminhão,Leve,Tarde,Final de Semana/Feriado,Padrão,Não
171,Longa,Limpo,Van,Leve,Tarde,Dia Útil,Frágil/Volume Especial,Não
172,Curta,Limpo,Van,Severo,Tarde,Dia Útil,Frágil/Volume Especial,Não
173,Longa,Tempestade/Alerta,Caminhão,Leve,Noite,Dia Útil,Padrão,Sim
174,Longa,Tempestade/Alerta,Caminhão,Leve,Tarde,Final de Semana/Feriado,Padrão,Sim
175,Curta,Limpo,Caminhão,Leve,Noite,Final de Semana/Feriado,Padrão,Não
176,Curta,Tempestade/Alerta,Van,Leve,Noite,Dia Útil,Frágil/Volume Especial,Não
177,Média,Chuva Leve,Moto,Leve,Manhã,Dia Útil,Padrão,Não
178,Média,Limpo,Van,Moderado,Manhã,Dia Útil,Padrão,Não
179,Média,Limpo,Caminhão,Leve,Noite,Dia Útil,Padrão,Não
180,Curta,Limpo,Caminhão,Leve,Tarde,Dia Útil,Padrão,Não
181,Longa,Limpo,Moto,Severo,Tarde,Dia Útil,Padrão,Sim
182,Média,Tempestade/Alerta,Caminhão,Moderado,Tarde,Dia Útil,Frágil/Volume Especial,Não
183,Média,Chuva Leve,Moto,Severo,Noite,Final de Semana/Feriado,Frágil/Volume Especial,Sim
184,Curta,Chuva Leve,Van,Moderado,Manhã,Dia Útil,Padrão,Não
185,Longa,Chuva Leve,Caminhão,Leve,Tarde,Final de Semana/Feriado,Frágil/Volume Especial,Não
186,Média,Tempestade/Alerta,Van,Leve,Manhã,Final de Semana/Feriado,Frágil/Volume Especial,Sim
187,Curta,Chuva Leve,Moto,Leve,Tarde,Final de Semana/Feriado,Padrão,Não
188,Média,Chuva Leve,Moto,Leve,Noite,Final de Semana/Feriado,Padrão,Não
189,Longa,Tempestade/Alerta,Caminhão,Leve,Manhã,Final de Semana/Feriado,Padrão,Não
190,Longa,Tempestade/Alerta,Moto,Leve,Manhã,Dia Útil,Frágil/Volume Especial,Sim
191,Curta,Limpo,Caminhão,Severo,Tarde,Final de Semana/Feriado,Padrão,Não
192,Curta,Tempestade/Alerta,Caminhão,Leve,Noite,Final de Semana/Feriado,Padrão,Não
193,Curta,Limpo,Van,Moderado,Noite,Final de Semana/Feriado,Frágil/Volume Especial,Não
194,Curta,Tempestade/Alerta,Caminhão,Severo,Manhã,Dia Útil,Frágil/Volume Especial,Sim
195,Longa,Chuva Leve,Caminhão,Leve,Noite,Final de Semana/Feriado,Frágil/Volume Especial,Não
196,Curta,Chuva Leve,Caminhão,Moderado,Noite,Final de Semana/Feriado,Padrão,Não
197,Média,Limpo,Van,Leve,Noite,Dia Útil,Padrão,Não
198,Curta,Chuva Leve,Moto,Severo,Manhã,Final de Semana/Feriado,Padrão,Não
199,Média,Limpo,Caminhão,Moderado,Noite,Dia Útil,Frágil/Volume Especial,Não
200,Longa,Chuva Leve,Van,Moderado,Tarde,Final de Semana/Feriado,Padrão,Não
201,Longa,Chuva Leve,Van,Moderado,Noite,Final de Semana/Feriado,Padrão,Sim
202,Curta,Tempestade/Alerta,Van,Moderado,Noite,Dia Útil,Padrão,Sim
203,Média,Limpo,Van,Severo,Manhã,Dia Útil,Padrão,Sim
204,Curta,Chuva Leve,Van,Leve,Manhã,Final de Semana/Feriado,Padrão,Não
205,Longa,Limpo,Van,Leve,Manhã,Final de Semana/Feriado,Padrão,Não
206,Curta,Tempestade/Alerta,Caminhão,Leve,Noite,Dia Útil,Frágil/Volume Especial,Sim
207,Curta,Limpo,Van,Severo,Tarde,Dia Útil,Frágil/Volume Especial,Não
208,Curta,Limpo,Moto,Moderado,Tarde,Final de Semana/Feriado,Padrão,Não
209,Média,Chuva Leve,Moto,Leve,Tarde,Dia Útil,Padrão,Não
210,Longa,Chuva Leve,Caminhão,Leve,Noite,Dia Útil,Padrão,Não
211,Longa,Limpo,Van,Moderado,Tarde,Final de Semana/Feriado,Frágil/Volume Especial,Não
212,Curta,Limpo,Van,Severo,Tarde,Final de Semana/Feriado,Frágil/Volume Especial,Não
213,Longa,Limpo,Caminhão,Leve,Tarde,Dia Útil,Padrão,Sim
214,Curta,Chuva Leve,Moto,Leve,Noite,Final de Semana/Feriado,Padrão,Não
215,Curta,Chuva Leve,Van,Leve,Manhã,Dia Útil,Frágil/Volume Especial,Não
216,Média,Limpo,Caminhão,Severo,Manhã,Dia Útil,Padrão,Não
217,Curta,Limpo,Moto,Leve,Noite,Final de Semana/Feriado,Frágil/Volume Especial,Não
218,Longa,Chuva Leve,Caminhão,Leve,Manhã,Final de Semana/Feriado,Padrão,Não
219,Longa,Limpo,Caminhão,Leve,Tarde,Dia Útil,Padrão,Não
220,Curta,Limpo,Caminhão,Moderado,Noite,Dia Útil,Frágil/Volume Especial,Sim
221,Curta,Limpo,Caminhão,Moderado,Noite,Final de Semana/Feriado,Frágil/Volume Especial,Não
222,Curta,Tempestade/Alerta,Caminhão,Moderado,Manhã,Final de Semana/Feriado,Frágil/Volume Especial,Sim
223,Curta,Chuva Leve,Moto,Severo,Manhã,Dia Útil,Frágil/Volume Especial,Sim
224,Média,Tempestade/Alerta,Caminhão,Leve,Manhã,Dia Útil,Padrão,Não
225,Longa,Limpo,Van,Leve,Manhã,Final de Semana/Feriado,Padrão,Não
226,Longa,Chuva Leve,Van,Leve,Noite,Final de Semana/Feriado,Frágil/Volume Especial,Não
227,Média,Tempestade/Alerta,Caminhão,Severo,Tarde,Dia Útil,Frágil/Volume Especial,Sim
228,Longa,Tempestade/Alerta,Caminhão,Leve,Manhã,Dia Útil,Padrão,Não
229,Média,Tempestade/Alerta,Van,Moderado,Tarde,Final de Semana/Feriado,Frágil/Volume Especial,Sim
230,Média,Chuva Leve,Moto,Leve,Tarde,Final de Semana/Feriado,Padrão,Sim
231,Média,Chuva Leve,Caminhão,Moderado,Manhã,Final de Semana/Feriado,Frágil/Volume Especial,Não
232,Média,Tempestade/Alerta,Van,Leve,Noite,Final de Semana/Feriado,Padrão,Não
233,Curta,Chuva Leve,Van,Leve,Manhã,Dia Útil,Padrão,Não
234,Curta,Limpo,Caminhão,Moderado,Manhã,Final de Semana/Feriado,Padrão,Não
235,Média,Chuva Leve,Van,Moderado,Tarde,Dia Útil,Frágil/Volume Especial,Sim
236,Curta,Chuva Leve,Van,Moderado,Tarde,Dia Útil,Padrão,Não
237,Longa,Tempestade/Alerta,Van,Severo,Noite,Dia Útil,Padrão,Sim
238,Média,Tempestade/Alerta,Caminhão,Moderado,Manhã,Dia Útil,Frágil/Volume Especial,Sim
239,Longa,Limpo,Moto,Moderado,Noite,Final de Semana/Feriado,Padrão,Sim
240,Curta,Chuva Leve,Van,Severo,Tarde,Dia Útil,Frágil/Volume Especial,Sim

```


---

## Arquivo: `03_Dataset/gerar_dataset.py`

```py
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

with open("/home/claude/proj/03_Dataset/treinamento_logistica.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "distancia", "clima", "veiculo", "transito", "turno", "dia_semana", "tipo_carga", "atraso"])
    for i, r in enumerate(final, 1):
        w.writerow([i, *r])

print(f"Gerados {len(final)} registros | Sim: {sum(1 for r in final if r[-1]=='Sim')} | Não: {sum(1 for r in final if r[-1]=='Não')}")

```


---

## Arquivo: `04_Codigo_SQL/01_massa_dados.sql`

```sql
-- Massa de dados de treinamento: Classificador Bayesiano de Atrasos em Entregas (Logística)
-- 240 registros | Distribuição: 162 'Não' (67.5%) / 78 'Sim' (32.5%)

CREATE TABLE IF NOT EXISTS treinamento_logistica (
    id INTEGER PRIMARY KEY,
    distancia TEXT NOT NULL,
    clima TEXT NOT NULL,
    veiculo TEXT NOT NULL,
    transito TEXT NOT NULL,
    turno TEXT NOT NULL,
    dia_semana TEXT NOT NULL,
    tipo_carga TEXT NOT NULL,
    atraso TEXT NOT NULL CHECK (atraso IN ('Sim','Não'))
);

INSERT INTO treinamento_logistica (id, distancia, clima, veiculo, transito, turno, dia_semana, tipo_carga, atraso) VALUES
(1, 'Curta', 'Chuva Leve', 'Caminhão', 'Leve', 'Noite', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(2, 'Longa', 'Limpo', 'Van', 'Moderado', 'Manhã', 'Dia Útil', 'Padrão', 'Sim'),
(3, 'Longa', 'Tempestade/Alerta', 'Van', 'Leve', 'Noite', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(4, 'Longa', 'Limpo', 'Caminhão', 'Moderado', 'Noite', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(5, 'Curta', 'Tempestade/Alerta', 'Caminhão', 'Severo', 'Tarde', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Sim'),
(6, 'Média', 'Chuva Leve', 'Van', 'Moderado', 'Tarde', 'Dia Útil', 'Padrão', 'Não'),
(7, 'Longa', 'Limpo', 'Caminhão', 'Leve', 'Noite', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(8, 'Curta', 'Limpo', 'Caminhão', 'Leve', 'Manhã', 'Dia Útil', 'Padrão', 'Não'),
(9, 'Longa', 'Tempestade/Alerta', 'Van', 'Severo', 'Noite', 'Dia Útil', 'Padrão', 'Sim'),
(10, 'Média', 'Limpo', 'Van', 'Moderado', 'Tarde', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(11, 'Curta', 'Limpo', 'Moto', 'Severo', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(12, 'Longa', 'Limpo', 'Van', 'Leve', 'Manhã', 'Dia Útil', 'Padrão', 'Não'),
(13, 'Média', 'Limpo', 'Moto', 'Moderado', 'Manhã', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(14, 'Curta', 'Limpo', 'Caminhão', 'Moderado', 'Manhã', 'Dia Útil', 'Padrão', 'Não'),
(15, 'Longa', 'Tempestade/Alerta', 'Moto', 'Severo', 'Noite', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Sim'),
(16, 'Média', 'Tempestade/Alerta', 'Van', 'Severo', 'Tarde', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Sim'),
(17, 'Média', 'Chuva Leve', 'Moto', 'Leve', 'Noite', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(18, 'Média', 'Limpo', 'Caminhão', 'Leve', 'Noite', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(19, 'Média', 'Limpo', 'Caminhão', 'Severo', 'Manhã', 'Dia Útil', 'Frágil/Volume Especial', 'Sim'),
(20, 'Média', 'Chuva Leve', 'Moto', 'Leve', 'Manhã', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(21, 'Média', 'Chuva Leve', 'Moto', 'Leve', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(22, 'Curta', 'Tempestade/Alerta', 'Van', 'Severo', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Sim'),
(23, 'Média', 'Limpo', 'Van', 'Leve', 'Noite', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(24, 'Média', 'Limpo', 'Caminhão', 'Moderado', 'Noite', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(25, 'Média', 'Tempestade/Alerta', 'Caminhão', 'Moderado', 'Noite', 'Dia Útil', 'Padrão', 'Sim'),
(26, 'Curta', 'Tempestade/Alerta', 'Caminhão', 'Leve', 'Tarde', 'Dia Útil', 'Padrão', 'Não'),
(27, 'Longa', 'Limpo', 'Caminhão', 'Moderado', 'Manhã', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(28, 'Curta', 'Chuva Leve', 'Van', 'Severo', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(29, 'Média', 'Limpo', 'Caminhão', 'Moderado', 'Tarde', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(30, 'Longa', 'Limpo', 'Caminhão', 'Moderado', 'Manhã', 'Dia Útil', 'Padrão', 'Não'),
(31, 'Média', 'Tempestade/Alerta', 'Van', 'Moderado', 'Noite', 'Final de Semana/Feriado', 'Padrão', 'Sim'),
(32, 'Média', 'Chuva Leve', 'Moto', 'Leve', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(33, 'Média', 'Limpo', 'Caminhão', 'Leve', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(34, 'Média', 'Limpo', 'Moto', 'Moderado', 'Manhã', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(35, 'Curta', 'Tempestade/Alerta', 'Caminhão', 'Leve', 'Noite', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Sim'),
(36, 'Longa', 'Chuva Leve', 'Caminhão', 'Leve', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(37, 'Curta', 'Chuva Leve', 'Caminhão', 'Leve', 'Noite', 'Dia Útil', 'Padrão', 'Não'),
(38, 'Longa', 'Tempestade/Alerta', 'Caminhão', 'Moderado', 'Manhã', 'Dia Útil', 'Frágil/Volume Especial', 'Sim'),
(39, 'Longa', 'Limpo', 'Van', 'Leve', 'Noite', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(40, 'Média', 'Limpo', 'Moto', 'Moderado', 'Tarde', 'Dia Útil', 'Padrão', 'Não'),
(41, 'Média', 'Chuva Leve', 'Moto', 'Leve', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(42, 'Curta', 'Limpo', 'Van', 'Leve', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(43, 'Longa', 'Chuva Leve', 'Van', 'Moderado', 'Noite', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Sim'),
(44, 'Média', 'Chuva Leve', 'Caminhão', 'Leve', 'Noite', 'Dia Útil', 'Padrão', 'Não'),
(45, 'Média', 'Tempestade/Alerta', 'Caminhão', 'Severo', 'Manhã', 'Dia Útil', 'Padrão', 'Sim'),
(46, 'Média', 'Chuva Leve', 'Moto', 'Leve', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(47, 'Curta', 'Limpo', 'Moto', 'Moderado', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(48, 'Curta', 'Limpo', 'Van', 'Leve', 'Manhã', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(49, 'Longa', 'Limpo', 'Moto', 'Severo', 'Tarde', 'Dia Útil', 'Padrão', 'Sim'),
(50, 'Curta', 'Limpo', 'Van', 'Moderado', 'Noite', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(51, 'Média', 'Limpo', 'Van', 'Moderado', 'Noite', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Sim'),
(52, 'Média', 'Chuva Leve', 'Van', 'Moderado', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(53, 'Curta', 'Chuva Leve', 'Van', 'Moderado', 'Tarde', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(54, 'Longa', 'Limpo', 'Caminhão', 'Leve', 'Manhã', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(55, 'Curta', 'Chuva Leve', 'Van', 'Moderado', 'Noite', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(56, 'Curta', 'Chuva Leve', 'Van', 'Leve', 'Tarde', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(57, 'Curta', 'Chuva Leve', 'Moto', 'Moderado', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(58, 'Média', 'Tempestade/Alerta', 'Van', 'Severo', 'Manhã', 'Dia Útil', 'Frágil/Volume Especial', 'Sim'),
(59, 'Média', 'Chuva Leve', 'Van', 'Severo', 'Tarde', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(60, 'Curta', 'Chuva Leve', 'Caminhão', 'Moderado', 'Noite', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(61, 'Curta', 'Tempestade/Alerta', 'Van', 'Severo', 'Tarde', 'Dia Útil', 'Frágil/Volume Especial', 'Sim'),
(62, 'Curta', 'Chuva Leve', 'Moto', 'Moderado', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(63, 'Média', 'Chuva Leve', 'Moto', 'Moderado', 'Tarde', 'Dia Útil', 'Frágil/Volume Especial', 'Sim'),
(64, 'Média', 'Limpo', 'Van', 'Moderado', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(65, 'Curta', 'Chuva Leve', 'Van', 'Leve', 'Tarde', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(66, 'Média', 'Limpo', 'Caminhão', 'Moderado', 'Noite', 'Dia Útil', 'Padrão', 'Não'),
(67, 'Curta', 'Tempestade/Alerta', 'Caminhão', 'Severo', 'Manhã', 'Dia Útil', 'Padrão', 'Sim'),
(68, 'Média', 'Limpo', 'Moto', 'Moderado', 'Tarde', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(69, 'Curta', 'Chuva Leve', 'Van', 'Severo', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Sim'),
(70, 'Média', 'Limpo', 'Moto', 'Leve', 'Manhã', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(71, 'Curta', 'Limpo', 'Caminhão', 'Leve', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(72, 'Curta', 'Tempestade/Alerta', 'Caminhão', 'Severo', 'Noite', 'Dia Útil', 'Frágil/Volume Especial', 'Sim'),
(73, 'Média', 'Tempestade/Alerta', 'Moto', 'Leve', 'Tarde', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Sim'),
(74, 'Curta', 'Chuva Leve', 'Moto', 'Moderado', 'Manhã', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(75, 'Curta', 'Chuva Leve', 'Moto', 'Moderado', 'Noite', 'Final de Semana/Feriado', 'Padrão', 'Sim'),
(76, 'Longa', 'Chuva Leve', 'Caminhão', 'Severo', 'Tarde', 'Dia Útil', 'Frágil/Volume Especial', 'Sim'),
(77, 'Média', 'Chuva Leve', 'Van', 'Moderado', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(78, 'Longa', 'Chuva Leve', 'Caminhão', 'Leve', 'Noite', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(79, 'Média', 'Limpo', 'Caminhão', 'Leve', 'Noite', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(80, 'Média', 'Limpo', 'Caminhão', 'Moderado', 'Manhã', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(81, 'Média', 'Chuva Leve', 'Caminhão', 'Leve', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(82, 'Média', 'Chuva Leve', 'Moto', 'Severo', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Sim'),
(83, 'Longa', 'Tempestade/Alerta', 'Moto', 'Moderado', 'Tarde', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Sim'),
(84, 'Média', 'Limpo', 'Van', 'Leve', 'Noite', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(85, 'Longa', 'Tempestade/Alerta', 'Van', 'Moderado', 'Noite', 'Final de Semana/Feriado', 'Padrão', 'Sim'),
(86, 'Longa', 'Chuva Leve', 'Moto', 'Leve', 'Noite', 'Dia Útil', 'Padrão', 'Não'),
(87, 'Média', 'Tempestade/Alerta', 'Caminhão', 'Moderado', 'Manhã', 'Dia Útil', 'Padrão', 'Não'),
(88, 'Curta', 'Limpo', 'Caminhão', 'Moderado', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(89, 'Curta', 'Limpo', 'Van', 'Leve', 'Noite', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(90, 'Curta', 'Chuva Leve', 'Moto', 'Leve', 'Manhã', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(91, 'Longa', 'Tempestade/Alerta', 'Van', 'Moderado', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Sim'),
(92, 'Longa', 'Chuva Leve', 'Moto', 'Severo', 'Noite', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Sim'),
(93, 'Curta', 'Chuva Leve', 'Moto', 'Severo', 'Noite', 'Dia Útil', 'Padrão', 'Sim'),
(94, 'Média', 'Chuva Leve', 'Caminhão', 'Moderado', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(95, 'Curta', 'Tempestade/Alerta', 'Caminhão', 'Leve', 'Noite', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Sim'),
(96, 'Curta', 'Chuva Leve', 'Caminhão', 'Moderado', 'Tarde', 'Dia Útil', 'Padrão', 'Não'),
(97, 'Longa', 'Chuva Leve', 'Caminhão', 'Severo', 'Tarde', 'Dia Útil', 'Frágil/Volume Especial', 'Sim'),
(98, 'Longa', 'Limpo', 'Van', 'Moderado', 'Noite', 'Final de Semana/Feriado', 'Padrão', 'Sim'),
(99, 'Curta', 'Chuva Leve', 'Caminhão', 'Leve', 'Noite', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(100, 'Longa', 'Tempestade/Alerta', 'Moto', 'Severo', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Sim'),
(101, 'Longa', 'Tempestade/Alerta', 'Moto', 'Leve', 'Noite', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Sim'),
(102, 'Média', 'Limpo', 'Caminhão', 'Moderado', 'Tarde', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(103, 'Longa', 'Limpo', 'Caminhão', 'Moderado', 'Tarde', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(104, 'Média', 'Limpo', 'Van', 'Leve', 'Noite', 'Dia Útil', 'Padrão', 'Não'),
(105, 'Média', 'Tempestade/Alerta', 'Caminhão', 'Moderado', 'Noite', 'Dia Útil', 'Frágil/Volume Especial', 'Sim'),
(106, 'Curta', 'Tempestade/Alerta', 'Caminhão', 'Moderado', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(107, 'Curta', 'Tempestade/Alerta', 'Moto', 'Moderado', 'Tarde', 'Dia Útil', 'Frágil/Volume Especial', 'Sim'),
(108, 'Média', 'Limpo', 'Moto', 'Moderado', 'Manhã', 'Dia Útil', 'Frágil/Volume Especial', 'Sim'),
(109, 'Curta', 'Tempestade/Alerta', 'Moto', 'Severo', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Sim'),
(110, 'Curta', 'Limpo', 'Van', 'Moderado', 'Tarde', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(111, 'Longa', 'Limpo', 'Caminhão', 'Moderado', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(112, 'Curta', 'Chuva Leve', 'Van', 'Leve', 'Noite', 'Dia Útil', 'Padrão', 'Não'),
(113, 'Curta', 'Chuva Leve', 'Caminhão', 'Leve', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(114, 'Média', 'Limpo', 'Caminhão', 'Moderado', 'Tarde', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(115, 'Longa', 'Limpo', 'Caminhão', 'Moderado', 'Noite', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Sim'),
(116, 'Média', 'Chuva Leve', 'Moto', 'Moderado', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(117, 'Longa', 'Tempestade/Alerta', 'Moto', 'Leve', 'Tarde', 'Dia Útil', 'Padrão', 'Sim'),
(118, 'Longa', 'Limpo', 'Moto', 'Leve', 'Tarde', 'Dia Útil', 'Padrão', 'Não'),
(119, 'Longa', 'Chuva Leve', 'Moto', 'Severo', 'Manhã', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Sim'),
(120, 'Média', 'Limpo', 'Moto', 'Leve', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(121, 'Média', 'Chuva Leve', 'Caminhão', 'Severo', 'Manhã', 'Dia Útil', 'Frágil/Volume Especial', 'Sim'),
(122, 'Curta', 'Tempestade/Alerta', 'Van', 'Leve', 'Manhã', 'Dia Útil', 'Padrão', 'Não'),
(123, 'Longa', 'Chuva Leve', 'Caminhão', 'Moderado', 'Noite', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(124, 'Curta', 'Limpo', 'Moto', 'Moderado', 'Tarde', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(125, 'Média', 'Limpo', 'Moto', 'Moderado', 'Manhã', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(126, 'Média', 'Limpo', 'Van', 'Moderado', 'Noite', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(127, 'Longa', 'Limpo', 'Moto', 'Moderado', 'Tarde', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Sim'),
(128, 'Curta', 'Chuva Leve', 'Caminhão', 'Leve', 'Manhã', 'Dia Útil', 'Padrão', 'Não'),
(129, 'Curta', 'Limpo', 'Moto', 'Leve', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(130, 'Média', 'Chuva Leve', 'Caminhão', 'Leve', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(131, 'Longa', 'Limpo', 'Moto', 'Moderado', 'Noite', 'Dia Útil', 'Padrão', 'Sim'),
(132, 'Média', 'Limpo', 'Van', 'Moderado', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(133, 'Média', 'Chuva Leve', 'Moto', 'Severo', 'Noite', 'Dia Útil', 'Frágil/Volume Especial', 'Sim'),
(134, 'Curta', 'Limpo', 'Van', 'Leve', 'Tarde', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(135, 'Longa', 'Chuva Leve', 'Caminhão', 'Moderado', 'Manhã', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(136, 'Longa', 'Limpo', 'Van', 'Moderado', 'Noite', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(137, 'Curta', 'Tempestade/Alerta', 'Caminhão', 'Leve', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(138, 'Média', 'Chuva Leve', 'Caminhão', 'Moderado', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(139, 'Curta', 'Chuva Leve', 'Caminhão', 'Leve', 'Manhã', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(140, 'Curta', 'Limpo', 'Moto', 'Leve', 'Noite', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(141, 'Curta', 'Limpo', 'Van', 'Moderado', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Sim'),
(142, 'Curta', 'Chuva Leve', 'Moto', 'Moderado', 'Noite', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(143, 'Curta', 'Tempestade/Alerta', 'Caminhão', 'Moderado', 'Manhã', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(144, 'Média', 'Limpo', 'Moto', 'Moderado', 'Noite', 'Dia Útil', 'Padrão', 'Não'),
(145, 'Média', 'Limpo', 'Caminhão', 'Moderado', 'Manhã', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(146, 'Média', 'Tempestade/Alerta', 'Moto', 'Severo', 'Noite', 'Dia Útil', 'Padrão', 'Sim'),
(147, 'Curta', 'Chuva Leve', 'Caminhão', 'Leve', 'Noite', 'Dia Útil', 'Padrão', 'Não'),
(148, 'Média', 'Chuva Leve', 'Van', 'Leve', 'Manhã', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(149, 'Longa', 'Limpo', 'Caminhão', 'Severo', 'Tarde', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Sim'),
(150, 'Média', 'Limpo', 'Van', 'Leve', 'Noite', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(151, 'Longa', 'Chuva Leve', 'Van', 'Moderado', 'Tarde', 'Dia Útil', 'Padrão', 'Não'),
(152, 'Curta', 'Limpo', 'Van', 'Severo', 'Tarde', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(153, 'Longa', 'Tempestade/Alerta', 'Caminhão', 'Moderado', 'Noite', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(154, 'Longa', 'Limpo', 'Caminhão', 'Leve', 'Tarde', 'Dia Útil', 'Padrão', 'Não'),
(155, 'Longa', 'Tempestade/Alerta', 'Caminhão', 'Leve', 'Tarde', 'Dia Útil', 'Frágil/Volume Especial', 'Sim'),
(156, 'Média', 'Tempestade/Alerta', 'Van', 'Severo', 'Tarde', 'Dia Útil', 'Padrão', 'Sim'),
(157, 'Média', 'Limpo', 'Van', 'Leve', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(158, 'Curta', 'Tempestade/Alerta', 'Moto', 'Severo', 'Manhã', 'Dia Útil', 'Padrão', 'Sim'),
(159, 'Longa', 'Tempestade/Alerta', 'Moto', 'Severo', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Sim'),
(160, 'Curta', 'Chuva Leve', 'Caminhão', 'Severo', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(161, 'Curta', 'Chuva Leve', 'Caminhão', 'Moderado', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(162, 'Curta', 'Tempestade/Alerta', 'Caminhão', 'Leve', 'Manhã', 'Dia Útil', 'Padrão', 'Sim'),
(163, 'Média', 'Chuva Leve', 'Caminhão', 'Moderado', 'Tarde', 'Dia Útil', 'Padrão', 'Não'),
(164, 'Curta', 'Chuva Leve', 'Caminhão', 'Leve', 'Tarde', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(165, 'Curta', 'Tempestade/Alerta', 'Caminhão', 'Moderado', 'Manhã', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(166, 'Média', 'Tempestade/Alerta', 'Caminhão', 'Moderado', 'Manhã', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(167, 'Curta', 'Tempestade/Alerta', 'Van', 'Moderado', 'Manhã', 'Dia Útil', 'Frágil/Volume Especial', 'Sim'),
(168, 'Curta', 'Chuva Leve', 'Van', 'Leve', 'Tarde', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(169, 'Curta', 'Limpo', 'Moto', 'Leve', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(170, 'Média', 'Tempestade/Alerta', 'Caminhão', 'Leve', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(171, 'Longa', 'Limpo', 'Van', 'Leve', 'Tarde', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(172, 'Curta', 'Limpo', 'Van', 'Severo', 'Tarde', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(173, 'Longa', 'Tempestade/Alerta', 'Caminhão', 'Leve', 'Noite', 'Dia Útil', 'Padrão', 'Sim'),
(174, 'Longa', 'Tempestade/Alerta', 'Caminhão', 'Leve', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Sim'),
(175, 'Curta', 'Limpo', 'Caminhão', 'Leve', 'Noite', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(176, 'Curta', 'Tempestade/Alerta', 'Van', 'Leve', 'Noite', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(177, 'Média', 'Chuva Leve', 'Moto', 'Leve', 'Manhã', 'Dia Útil', 'Padrão', 'Não'),
(178, 'Média', 'Limpo', 'Van', 'Moderado', 'Manhã', 'Dia Útil', 'Padrão', 'Não'),
(179, 'Média', 'Limpo', 'Caminhão', 'Leve', 'Noite', 'Dia Útil', 'Padrão', 'Não'),
(180, 'Curta', 'Limpo', 'Caminhão', 'Leve', 'Tarde', 'Dia Útil', 'Padrão', 'Não'),
(181, 'Longa', 'Limpo', 'Moto', 'Severo', 'Tarde', 'Dia Útil', 'Padrão', 'Sim'),
(182, 'Média', 'Tempestade/Alerta', 'Caminhão', 'Moderado', 'Tarde', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(183, 'Média', 'Chuva Leve', 'Moto', 'Severo', 'Noite', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Sim'),
(184, 'Curta', 'Chuva Leve', 'Van', 'Moderado', 'Manhã', 'Dia Útil', 'Padrão', 'Não'),
(185, 'Longa', 'Chuva Leve', 'Caminhão', 'Leve', 'Tarde', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(186, 'Média', 'Tempestade/Alerta', 'Van', 'Leve', 'Manhã', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Sim'),
(187, 'Curta', 'Chuva Leve', 'Moto', 'Leve', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(188, 'Média', 'Chuva Leve', 'Moto', 'Leve', 'Noite', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(189, 'Longa', 'Tempestade/Alerta', 'Caminhão', 'Leve', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(190, 'Longa', 'Tempestade/Alerta', 'Moto', 'Leve', 'Manhã', 'Dia Útil', 'Frágil/Volume Especial', 'Sim'),
(191, 'Curta', 'Limpo', 'Caminhão', 'Severo', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(192, 'Curta', 'Tempestade/Alerta', 'Caminhão', 'Leve', 'Noite', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(193, 'Curta', 'Limpo', 'Van', 'Moderado', 'Noite', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(194, 'Curta', 'Tempestade/Alerta', 'Caminhão', 'Severo', 'Manhã', 'Dia Útil', 'Frágil/Volume Especial', 'Sim'),
(195, 'Longa', 'Chuva Leve', 'Caminhão', 'Leve', 'Noite', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(196, 'Curta', 'Chuva Leve', 'Caminhão', 'Moderado', 'Noite', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(197, 'Média', 'Limpo', 'Van', 'Leve', 'Noite', 'Dia Útil', 'Padrão', 'Não'),
(198, 'Curta', 'Chuva Leve', 'Moto', 'Severo', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(199, 'Média', 'Limpo', 'Caminhão', 'Moderado', 'Noite', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(200, 'Longa', 'Chuva Leve', 'Van', 'Moderado', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(201, 'Longa', 'Chuva Leve', 'Van', 'Moderado', 'Noite', 'Final de Semana/Feriado', 'Padrão', 'Sim'),
(202, 'Curta', 'Tempestade/Alerta', 'Van', 'Moderado', 'Noite', 'Dia Útil', 'Padrão', 'Sim'),
(203, 'Média', 'Limpo', 'Van', 'Severo', 'Manhã', 'Dia Útil', 'Padrão', 'Sim'),
(204, 'Curta', 'Chuva Leve', 'Van', 'Leve', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(205, 'Longa', 'Limpo', 'Van', 'Leve', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(206, 'Curta', 'Tempestade/Alerta', 'Caminhão', 'Leve', 'Noite', 'Dia Útil', 'Frágil/Volume Especial', 'Sim'),
(207, 'Curta', 'Limpo', 'Van', 'Severo', 'Tarde', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(208, 'Curta', 'Limpo', 'Moto', 'Moderado', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(209, 'Média', 'Chuva Leve', 'Moto', 'Leve', 'Tarde', 'Dia Útil', 'Padrão', 'Não'),
(210, 'Longa', 'Chuva Leve', 'Caminhão', 'Leve', 'Noite', 'Dia Útil', 'Padrão', 'Não'),
(211, 'Longa', 'Limpo', 'Van', 'Moderado', 'Tarde', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(212, 'Curta', 'Limpo', 'Van', 'Severo', 'Tarde', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(213, 'Longa', 'Limpo', 'Caminhão', 'Leve', 'Tarde', 'Dia Útil', 'Padrão', 'Sim'),
(214, 'Curta', 'Chuva Leve', 'Moto', 'Leve', 'Noite', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(215, 'Curta', 'Chuva Leve', 'Van', 'Leve', 'Manhã', 'Dia Útil', 'Frágil/Volume Especial', 'Não'),
(216, 'Média', 'Limpo', 'Caminhão', 'Severo', 'Manhã', 'Dia Útil', 'Padrão', 'Não'),
(217, 'Curta', 'Limpo', 'Moto', 'Leve', 'Noite', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(218, 'Longa', 'Chuva Leve', 'Caminhão', 'Leve', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(219, 'Longa', 'Limpo', 'Caminhão', 'Leve', 'Tarde', 'Dia Útil', 'Padrão', 'Não'),
(220, 'Curta', 'Limpo', 'Caminhão', 'Moderado', 'Noite', 'Dia Útil', 'Frágil/Volume Especial', 'Sim'),
(221, 'Curta', 'Limpo', 'Caminhão', 'Moderado', 'Noite', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(222, 'Curta', 'Tempestade/Alerta', 'Caminhão', 'Moderado', 'Manhã', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Sim'),
(223, 'Curta', 'Chuva Leve', 'Moto', 'Severo', 'Manhã', 'Dia Útil', 'Frágil/Volume Especial', 'Sim'),
(224, 'Média', 'Tempestade/Alerta', 'Caminhão', 'Leve', 'Manhã', 'Dia Útil', 'Padrão', 'Não'),
(225, 'Longa', 'Limpo', 'Van', 'Leve', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(226, 'Longa', 'Chuva Leve', 'Van', 'Leve', 'Noite', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(227, 'Média', 'Tempestade/Alerta', 'Caminhão', 'Severo', 'Tarde', 'Dia Útil', 'Frágil/Volume Especial', 'Sim'),
(228, 'Longa', 'Tempestade/Alerta', 'Caminhão', 'Leve', 'Manhã', 'Dia Útil', 'Padrão', 'Não'),
(229, 'Média', 'Tempestade/Alerta', 'Van', 'Moderado', 'Tarde', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Sim'),
(230, 'Média', 'Chuva Leve', 'Moto', 'Leve', 'Tarde', 'Final de Semana/Feriado', 'Padrão', 'Sim'),
(231, 'Média', 'Chuva Leve', 'Caminhão', 'Moderado', 'Manhã', 'Final de Semana/Feriado', 'Frágil/Volume Especial', 'Não'),
(232, 'Média', 'Tempestade/Alerta', 'Van', 'Leve', 'Noite', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(233, 'Curta', 'Chuva Leve', 'Van', 'Leve', 'Manhã', 'Dia Útil', 'Padrão', 'Não'),
(234, 'Curta', 'Limpo', 'Caminhão', 'Moderado', 'Manhã', 'Final de Semana/Feriado', 'Padrão', 'Não'),
(235, 'Média', 'Chuva Leve', 'Van', 'Moderado', 'Tarde', 'Dia Útil', 'Frágil/Volume Especial', 'Sim'),
(236, 'Curta', 'Chuva Leve', 'Van', 'Moderado', 'Tarde', 'Dia Útil', 'Padrão', 'Não'),
(237, 'Longa', 'Tempestade/Alerta', 'Van', 'Severo', 'Noite', 'Dia Útil', 'Padrão', 'Sim'),
(238, 'Média', 'Tempestade/Alerta', 'Caminhão', 'Moderado', 'Manhã', 'Dia Útil', 'Frágil/Volume Especial', 'Sim'),
(239, 'Longa', 'Limpo', 'Moto', 'Moderado', 'Noite', 'Final de Semana/Feriado', 'Padrão', 'Sim'),
(240, 'Curta', 'Chuva Leve', 'Van', 'Severo', 'Tarde', 'Dia Útil', 'Frágil/Volume Especial', 'Sim');
```


---

## Arquivo: `04_Codigo_SQL/02_classificador_bayesiano.sql`

```sql
-- =====================================================================
-- Classificador Naive Bayes (SQL) - Previsão de Atraso na Entrega
-- Domínio: Logística
-- Requer a tabela treinamento_logistica (ver 01_massa_dados.sql)
-- =====================================================================

-- ETAPA A: Definição do novo caso a ser classificado
-- (troque os valores aqui para testar outro perfil - ver 05_Testes_e_Resultados)
WITH novo_caso AS (
    SELECT
        :v_distancia   AS v_distancia,
        :v_clima       AS v_clima,
        :v_veiculo     AS v_veiculo,
        :v_transito    AS v_transito,
        :v_turno       AS v_turno,
        :v_dia_semana  AS v_dia_semana,
        :v_tipo_carga  AS v_tipo_carga
),

-- ETAPA B: contagens base e tamanho do vocabulário de cada feature (para Laplace)
estatisticas_base AS (
    SELECT
        COUNT(*) AS total_registros,
        (SELECT COUNT(DISTINCT distancia)  FROM treinamento_logistica) AS V_distancia,
        (SELECT COUNT(DISTINCT clima)      FROM treinamento_logistica) AS V_clima,
        (SELECT COUNT(DISTINCT veiculo)    FROM treinamento_logistica) AS V_veiculo,
        (SELECT COUNT(DISTINCT transito)   FROM treinamento_logistica) AS V_transito,
        (SELECT COUNT(DISTINCT turno)      FROM treinamento_logistica) AS V_turno,
        (SELECT COUNT(DISTINCT dia_semana) FROM treinamento_logistica) AS V_dia_semana,
        (SELECT COUNT(DISTINCT tipo_carga) FROM treinamento_logistica) AS V_carga
    FROM treinamento_logistica
),

-- ETAPA C: probabilidade a priori P(classe), em log
priori AS (
    SELECT
        atraso,
        COUNT(*) AS qtd_classe,
        LN((COUNT(*) * 1.0) / MAX(e.total_registros)) AS log_priori
    FROM treinamento_logistica
    CROSS JOIN estatisticas_base e
    GROUP BY atraso
),

-- ETAPA D: verossimilhanças P(feature=valor | classe) com suavização de Laplace, em log
-- Fórmula de Laplace: (Contagem(feature=valor, classe) + 1) / (Total(classe) + |Vocabulário(feature)|)
verossimilhanca AS (
    SELECT
        p.atraso,
        p.log_priori,
        p.qtd_classe,
        LN((SUM(CASE WHEN t.distancia  = nc.v_distancia  THEN 1 ELSE 0 END) + 1.0) / (p.qtd_classe + e.V_distancia))  AS log_v_dist,
        LN((SUM(CASE WHEN t.clima      = nc.v_clima      THEN 1 ELSE 0 END) + 1.0) / (p.qtd_classe + e.V_clima))     AS log_v_clima,
        LN((SUM(CASE WHEN t.veiculo    = nc.v_veiculo    THEN 1 ELSE 0 END) + 1.0) / (p.qtd_classe + e.V_veiculo))   AS log_v_veiculo,
        LN((SUM(CASE WHEN t.transito   = nc.v_transito   THEN 1 ELSE 0 END) + 1.0) / (p.qtd_classe + e.V_transito))  AS log_v_transito,
        LN((SUM(CASE WHEN t.turno      = nc.v_turno      THEN 1 ELSE 0 END) + 1.0) / (p.qtd_classe + e.V_turno))     AS log_v_turno,
        LN((SUM(CASE WHEN t.dia_semana = nc.v_dia_semana THEN 1 ELSE 0 END) + 1.0) / (p.qtd_classe + e.V_dia_semana)) AS log_v_dia,
        LN((SUM(CASE WHEN t.tipo_carga = nc.v_tipo_carga THEN 1 ELSE 0 END) + 1.0) / (p.qtd_classe + e.V_carga))     AS log_v_carga
    FROM priori p
    LEFT JOIN treinamento_logistica t ON p.atraso = t.atraso
    CROSS JOIN novo_caso nc
    CROSS JOIN estatisticas_base e
    GROUP BY p.atraso, p.log_priori, p.qtd_classe, e.V_distancia, e.V_clima, e.V_veiculo,
             e.V_transito, e.V_turno, e.V_dia_semana, e.V_carga
),

-- ETAPA E: soma dos logs (evita underflow numérico) e reversão para escala normal (exp)
score_bruto AS (
    SELECT
        atraso,
        (log_priori + log_v_dist + log_v_clima + log_v_veiculo + log_v_transito + log_v_turno + log_v_dia + log_v_carga) AS log_score_final,
        EXP(log_priori + log_v_dist + log_v_clima + log_v_veiculo + log_v_transito + log_v_turno + log_v_dia + log_v_carga) AS score_exp
    FROM verossimilhanca
)

-- ETAPA F: normalização (0% a 100%) + recomendação de decisão
SELECT
    atraso AS Classe,
    ROUND(log_score_final, 4) AS Log_Score,
    ROUND((score_exp / SUM(score_exp) OVER()) * 100, 2) AS Probabilidade_Percentual,
    CASE
        WHEN atraso = 'Sim'
             AND (score_exp / SUM(score_exp) OVER()) * 100 = (
                 SELECT MAX(p2) FROM (
                     SELECT (score_exp / SUM(score_exp) OVER()) * 100 AS p2 FROM score_bruto
                 )
             )
        THEN 'RECOMENDAÇÃO: Acionar plano de contingência (troca de modal / priorização) - alto risco de SLA quebrado'
        WHEN atraso = 'Não'
             AND (score_exp / SUM(score_exp) OVER()) * 100 = (
                 SELECT MAX(p2) FROM (
                     SELECT (score_exp / SUM(score_exp) OVER()) * 100 AS p2 FROM score_bruto
                 )
             )
        THEN 'RECOMENDAÇÃO: Manter operação padrão - baixo risco de atraso'
        ELSE ''
    END AS Recomendacao
FROM score_bruto
ORDER BY Probabilidade_Percentual DESC;

```


---

## Arquivo: `05_Testes_e_Resultados/resultados_e_analise.md`

```md
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

```


---

## Arquivo: `05_Testes_e_Resultados/resultados_brutos.json`

```json
[
  {
    "caso": "Teste 1 - Alto Risco Extremo",
    "perfil": {
      "v_distancia": "Longa",
      "v_clima": "Tempestade/Alerta",
      "v_veiculo": "Moto",
      "v_transito": "Severo",
      "v_turno": "Noite",
      "v_dia_semana": "Dia Útil",
      "v_tipo_carga": "Frágil/Volume Especial"
    },
    "colunas": [
      "Classe",
      "Log_Score",
      "Probabilidade_Percentual",
      "Recomendacao"
    ],
    "linhas": [
      [
        "Sim",
        -6.6739,
        98.9,
        "RECOMENDAÇÃO: Acionar plano de contingência (troca de modal / priorização) - alto risco de SLA quebrado"
      ],
      [
        "Não",
        -11.1703,
        1.1,
        ""
      ]
    ]
  },
  {
    "caso": "Teste 2 - Cenário Ideal (baixo risco)",
    "perfil": {
      "v_distancia": "Curta",
      "v_clima": "Limpo",
      "v_veiculo": "Caminhão",
      "v_transito": "Leve",
      "v_turno": "Manhã",
      "v_dia_semana": "Dia Útil",
      "v_tipo_carga": "Padrão"
    },
    "colunas": [
      "Classe",
      "Log_Score",
      "Probabilidade_Percentual",
      "Recomendacao"
    ],
    "linhas": [
      [
        "Não",
        -5.8385,
        96.96,
        "RECOMENDAÇÃO: Manter operação padrão - baixo risco de atraso"
      ],
      [
        "Sim",
        -9.2993,
        3.04,
        ""
      ]
    ]
  },
  {
    "caso": "Teste 3 - Perfil Ambíguo",
    "perfil": {
      "v_distancia": "Média",
      "v_clima": "Chuva Leve",
      "v_veiculo": "Van",
      "v_transito": "Moderado",
      "v_turno": "Tarde",
      "v_dia_semana": "Final de Semana/Feriado",
      "v_tipo_carga": "Padrão"
    },
    "colunas": [
      "Classe",
      "Log_Score",
      "Probabilidade_Percentual",
      "Recomendacao"
    ],
    "linhas": [
      [
        "Não",
        -6.4213,
        89.94,
        "RECOMENDAÇÃO: Manter operação padrão - baixo risco de atraso"
      ],
      [
        "Sim",
        -8.6115,
        10.06,
        ""
      ]
    ]
  },
  {
    "caso": "Teste 4 - Fator Crítico: Trânsito",
    "perfil": {
      "v_distancia": "Curta",
      "v_clima": "Limpo",
      "v_veiculo": "Moto",
      "v_transito": "Severo",
      "v_turno": "Manhã",
      "v_dia_semana": "Dia Útil",
      "v_tipo_carga": "Padrão"
    },
    "colunas": [
      "Classe",
      "Log_Score",
      "Probabilidade_Percentual",
      "Recomendacao"
    ],
    "linhas": [
      [
        "Sim",
        -8.325,
        54.1,
        "RECOMENDAÇÃO: Acionar plano de contingência (troca de modal / priorização) - alto risco de SLA quebrado"
      ],
      [
        "Não",
        -8.4894,
        45.9,
        ""
      ]
    ]
  },
  {
    "caso": "Teste 5 - Fator Crítico: Clima",
    "perfil": {
      "v_distancia": "Longa",
      "v_clima": "Tempestade/Alerta",
      "v_veiculo": "Caminhão",
      "v_transito": "Leve",
      "v_turno": "Tarde",
      "v_dia_semana": "Final de Semana/Feriado",
      "v_tipo_carga": "Padrão"
    },
    "colunas": [
      "Classe",
      "Log_Score",
      "Probabilidade_Percentual",
      "Recomendacao"
    ],
    "linhas": [
      [
        "Não",
        -7.7427,
        58.47,
        "RECOMENDAÇÃO: Manter operação padrão - baixo risco de atraso"
      ],
      [
        "Sim",
        -8.0847,
        41.53,
        ""
      ]
    ]
  },
  {
    "caso": "Teste 6 - Valor Não Visto (Drone)",
    "perfil": {
      "v_distancia": "Longa",
      "v_clima": "Tempestade/Alerta",
      "v_veiculo": "Drone",
      "v_transito": "Severo",
      "v_turno": "Noite",
      "v_dia_semana": "Dia Útil",
      "v_tipo_carga": "Padrão"
    },
    "colunas": [
      "Classe",
      "Log_Score",
      "Probabilidade_Percentual",
      "Recomendacao"
    ],
    "linhas": [
      [
        "Sim",
        -10.2419,
        98.44,
        "RECOMENDAÇÃO: Acionar plano de contingência (troca de modal / priorização) - alto risco de SLA quebrado"
      ],
      [
        "Não",
        -14.3859,
        1.56,
        ""
      ]
    ]
  }
]
```


---

## Arquivo: `05_Testes_e_Resultados/log_odds.json`

```json
[
  [
    "transito",
    "Severo",
    1.838
  ],
  [
    "clima",
    "Tempestade/Alerta",
    1.574
  ],
  [
    "transito",
    "Leve",
    -1.023
  ],
  [
    "clima",
    "Limpo",
    -0.812
  ],
  [
    "distancia",
    "Longa",
    0.651
  ],
  [
    "clima",
    "Chuva Leve",
    -0.564
  ],
  [
    "veiculo",
    "Moto",
    0.468
  ],
  [
    "distancia",
    "Curta",
    -0.359
  ],
  [
    "tipo_carga",
    "Frágil/Volume Especial",
    0.312
  ],
  [
    "veiculo",
    "Caminhão",
    -0.297
  ],
  [
    "tipo_carga",
    "Padrão",
    -0.284
  ],
  [
    "dia_semana",
    "Final de Semana/Feriado",
    -0.198
  ],
  [
    "dia_semana",
    "Dia Útil",
    0.198
  ],
  [
    "turno",
    "Noite",
    0.187
  ],
  [
    "distancia",
    "Média",
    -0.181
  ],
  [
    "turno",
    "Manhã",
    -0.154
  ],
  [
    "transito",
    "Moderado",
    -0.141
  ],
  [
    "veiculo",
    "Van",
    -0.059
  ],
  [
    "turno",
    "Tarde",
    -0.034
  ]
]
```


---

## Arquivo: `06_Apresentacao/reflexao_critica.md`

```md
# Etapa 5 — Reflexão Crítica

O modelo Naive Bayes mostrou-se computacionalmente eficiente, processando as probabilidades
com rapidez via SQL e acertando as classificações dos extremos lógicos de risco (Testes 1 e 2)
com alta confiança. Sua principal falha, porém, é a premissa "ingênua" de **independência
condicional** entre as features. No mundo real da logística essa independência não existe: uma
"Tempestade" causa diretamente "Trânsito Severo". Ao tratar as duas features como
independentes, o modelo conta o mesmo risco duas vezes (uma pelo clima, outra
indiretamente pelo trânsito que a chuva gerou), o que pode superestimar a probabilidade de
atraso em cenários onde causa e efeito climático/trânsito coexistem. Uma limitação secundária
aparece no Teste 6: a suavização de Laplace evita o erro numérico com valores nunca vistos
("Drone"), mas atribui a esse valor a mesma probabilidade genérica de qualquer categoria
rara — o modelo não tem como saber que um drone provavelmente enfrenta um perfil de risco
completamente diferente de uma moto. Para mitigar essas limitações, algoritmos como Árvores
de Decisão ou Regressão Logística com termos de interação explícitos lidariam melhor com
relações cruzadas entre variáveis.

---

# Roteiro para a Apresentação Oral

O enunciado avisa: "submeter código que você não consegue explicar oralmente equivale a
não ter realizado a atividade" — use este roteiro para treinar, não para ler na hora.

1. **Domínio e rótulo (30s):** por que Logística, por que `Atraso_Na_Entrega` é binário e
   acionável (permite decisão automática de contingência).
2. **Features e discretização (1 min):** explicar por que cada feature foi discretizada em 2-3
   categorias (não contínua) — Naive Bayes categórico trabalha com contagens por categoria.
3. **Como os dados foram gerados (1 min):** explicar o score de risco ponderado + as duas
   regras de interação (Moto+Tempestade, Caminhão+Trânsito Severo) — deixe claro que não é
   aleatório puro, é gerado por regra de negócio com ruído controlado.
4. **O código SQL, CTE por CTE (2-3 min) — a parte mais cobrada:**
   - `novo_caso`: os parâmetros do perfil a classificar.
   - `estatisticas_base`: por que preciso do tamanho do vocabulário de cada feature (é o `V`
     da fórmula de Laplace).
   - `priori`: `P(classe) = contagem da classe / total`, em log.
   - `verossimilhanca`: a fórmula de Laplace exata — `(contagem+1)/(total_classe+V)` — e por
     que sem o "+1" uma categoria nunca vista zeraria toda a probabilidade da classe.
   - `score_bruto`: por que somamos logs em vez de multiplicar probabilidades diretamente
     (evita underflow numérico com muitas features).
   - normalização final: por que dividir pela soma dos `EXP()` das duas classes dá uma
     probabilidade percentual coerente (soma 100%).
5. **Resultados (1-2 min):** mostrar a tabela de `05_Testes_e_Resultados`, destacar o Teste 6
   (Drone) como prova de que a suavização de Laplace funciona.
6. **Log-odds (1 min):** por que Trânsito Severo e Tempestade são os fatores mais decisivos —
   consistente com a intuição da Etapa 1.
7. **Limitações (1 min):** a reflexão crítica acima — feche com isso.

```


---

## Arquivo: `README.md`

```md
# Atividade Prática 1 — Classificador Bayesiano (Logística)

Previsão de `Atraso_Na_Entrega` (Sim/Não) via Naive Bayes implementado em SQL puro.

## Estrutura

- **01_Prompts/** — diálogo documentado com a IA em cada etapa (modelagem, dados, código, testes).
- **02_Modelagem/** — Etapa 1: domínio, rótulo, features e discretização.
- **03_Dataset/** — Etapa 2: `treinamento_logistica.csv` (240 registros, 162 Não / 78 Sim) e o script que os gerou (`gerar_dataset.py`).
- **04_Codigo_SQL/** — Etapa 3: `01_massa_dados.sql` (CREATE TABLE + INSERTs) e `02_classificador_bayesiano.sql` (o classificador, parametrizado por `:v_feature`).
- **05_Testes_e_Resultados/** — Etapa 4: 6 casos de teste **executados de fato** contra o SQL (não estimados), com análise de log-odds.
- **06_Apresentacao/** — Etapa 5: reflexão crítica + roteiro para a defesa oral.
- **Atividade/Atividade.pdf** — enunciado original.

## Como rodar o classificador

O SQL usa parâmetros nomeados (`:v_distancia`, `:v_clima`, etc.), compatível com SQLite,
DuckDB ou qualquer client que suporte bind parameters. Exemplo em Python:

```python
import sqlite3
conn = sqlite3.connect("dados.db")
conn.executescript(open("04_Codigo_SQL/01_massa_dados.sql").read())
cur = conn.cursor()
cur.execute(open("04_Codigo_SQL/02_classificador_bayesiano.sql").read(), {
    "v_distancia": "Longa", "v_clima": "Tempestade/Alerta", "v_veiculo": "Moto",
    "v_transito": "Severo", "v_turno": "Noite", "v_dia_semana": "Dia Útil",
    "v_tipo_carga": "Frágil/Volume Especial"
})
print(cur.fetchall())
```

Se for rodar em Postgres/MySQL, troque `:nome` pela sintaxe de parâmetro do seu client
(`%(nome)s`, `?`, etc.) — a lógica das CTEs não muda.

```
