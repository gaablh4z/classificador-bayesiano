

# Documentação do Diálogo com IA Generativa




## Prompt 1 — Modelagem do problema (Etapa 1)

**Prompt utilizado:**
"Me ajude a modelar um problema de classificação binária com Naive Bayes focado no setor de Logística. Preciso de um rótulo alvo claro (Sim/Não) e de 6 a 8 variáveis com sentido prático real, divididas em categorias simples. Explique a lógica e a intuição de risco por trás de cada variável."

**O que aproveitamos e ajustamos:**
A IA sugeriu o rótulo `Atraso_Na_Entrega` e propôs 7 features (Distância, Clima, Veículo, Trânsito, Turno, Dia da Semana e Tipo de Carga). Adotamos a proposta por representar muito bem o dia a dia das transportadoras. A intuição de que combinações como "Tempestade + Trânsito Severo + Moto" aumentam drasticamente o risco de atraso guiou a nossa modelagem e mais tarde se confirmou no cálculo de log-odds.

## Prompt 2 — Geração da massa de dados (Etapa 2)

**Prompt utilizado:**
"Crie um script em Python para gerar 240 registros sintéticos baseados nessas 7 variáveis. A lógica de pontuação precisa ter regras intencionais (como Moto + Tempestade agravando bastante o risco) e uma margem de ruído realista para não ficar um dado artificial ou 100% previsível. Mantenha a proporção em cerca de 65-70% de entregas no prazo ('Não') e 30-35% de atrasos ('Sim')."

**O que aproveitamos e ajustamos:**
A IA sugeriu usar um score ponderado por variável com interações não lineares e uma função logística (sigmoide) com ruído aleatório. Nós calibramos manualmente os pesos e os limiares até atingir a distribuição exata de 240 registros (162 'Não' e 78 'Sim'), garantindo que a base tivesse variabilidade sem perder a coerência de negócio.

## Prompt 3 — Código do classificador em SQL (Etapa 3)

**Prompt utilizado:**
"Escreva o classificador Naive Bayes completo em SQL usando CTEs. O código precisa calcular a probabilidade a priori, as verossimilhanças com suavização de Laplace para cada feature, a soma em log das probabilidades para evitar underflow numérico, a normalização final para uma porcentagem de 0% a 100% e uma coluna de recomendação de decisão com base na classe vencedora."

**O que aproveitamos e ajustamos:**
A IA estruturou o SQL em blocos limpos (CTEs). Fizemos revisões importantes: adicionamos a coluna de `Recomendacao` de contingência operacional (essencial para o negócio), parametrizamos a entrada com `:v_feature` para rodar múltiplos testes sem alterar a consulta e validamos os cálculos na mão em Python para ter certeza absoluta de que a matemática de Laplace e a normalização estavam corretas.

## Prompt 4 — Interpretação dos testes e log-odds (Etapa 4)

**Prompt utilizado:**
"Vamos rodar o classificador para 6 perfis distintos: alto risco extremo, cenário ideal, perfil ambíguo, dois casos isolando fatores críticos (apenas trânsito severo e apenas tempestade) e um caso com veículo não visto no treino ('Drone'). Em seguida, calcule o log-odds de cada valor de feature para identificarmos quais variáveis têm maior poder discriminativo."

**O que aproveitamos e ajustamos:**
Executamos os 6 casos diretamente contra a base no banco de dados. Os resultados validaram a intuição: `Trânsito Severo` (+1.838) e `Tempestade` (+1.574) foram os fatores de maior impacto a favor do atraso. O teste do Drone comprovou na prática a eficácia da suavização de Laplace (o modelo não travou e classificou com base nas outras evidências), e o caso isolado de clima mostrou que o modelo é equilibrado e não toma decisões extremas com base em um único fator quando as outras variáveis são favoráveis.
