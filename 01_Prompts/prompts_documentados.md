# Diálogo com a IA Generativa — Documentação dos Prompts

> **Atividade Prática 1 — Algoritmo Classificador Bayesiano**  
> **Disciplina:** Mineração de Dados  
> **Domínio Escolhido:** Agronegócio (Previsão de Risco de Perda de Safra)

Este documento registra o histórico integral de diálogo com a IA generativa, detalhando os prompts utilizados para conceber a modelagem, a geração de dados, o algoritmo em SQL e a interpretação crítica dos resultados.

---

## Prompt 1 — Escolha do Domínio e Modelagem do Problema (Etapa 1)

### Prompt enviado à IA:
> *"Estamos realizando um trabalho de Mineração de Dados sobre Classificador Bayesiano. Escolhemos o domínio do **Agronegócio**, com foco em prever risco de perda de safra em fazendas de grãos para seguradoras agrícolas e bancos de crédito rural.*  
> *Preciso da sua ajuda para responder às 4 perguntas da Etapa 1 do trabalho:*  
> *1. Qual é o rótulo alvo (classificado como sim ou não)?*  
> *2. Quais são as 6 a 8 features mais relevantes e intuitivas para esse domínio (use nomes simples em português, fáceis de entender)?*  
> *3. Como discretizar cada feature em categorias significativas?*  
> *4. Qual é a lógica intuitiva por trás dos padrões de risco?"*

### Resumo da Resposta da IA:
1. **Rótulo Alvo:** `perda_safra` (`sim` / `nao`), onde `sim` representa uma queda de produtividade acima de 30% em relação à média histórica (acionamento do gatilho de seguro agrícola/PROAGRO).
2. **Features Selecionadas (7 variáveis simplificadas):**
   - `tipo_solo`: `argiloso`, `medio`, `arenoso`
   - `seca`: `nenhuma`, `moderada`, `severa`
   - `chuva`: `normal`, `excessiva`, `pouca`
   - `mes_plantio`: `outubro`, `novembro`, `dezembro`
   - `irrigacao`: `plantio_direto`, `convencional`, `irrigado`
   - `pragas`: `baixa`, `media`, `alta`
   - `regiao`: `planalto`, `transicao`, `baixada`
3. **Lógica Intuitiva:** 
   - Solos arenosos secam com poucos dias de estiagem, enquanto solos argilosos retêm umidade residual.
   - Seca severa no florescimento e enchimento de grãos é o principal causador de perdas.
   - Plantio tardio em dezembro empurra a safra para o final das chuvas e aumenta a incidência de pragas.
   - Irrigação artificial por pivô central consegue neutralizar a escassez de chuva.

---

## Prompt 2 — Geração da Massa de Treinamento em SQL (Etapa 2)

### Prompt enviado à IA:
> *"Com o modelo agronômico definido, elabore um gerador em Python que crie uma massa de dados de treinamento realista com mais de 100 registros (gere entre 300 e 1.000 registros para termos boa significância estatística).*  
> *Requisitos:*  
> *- Padrões intencionais e realistas (não aleatórios puros).*  
> *- Proporção coerente entre as classes (~20% a 25% de sinistros/perdas e ~75% a 80% de safras regulares).*  
> *- Salvar em script SQL (com CREATE TABLE e INSERTs), CSV e banco SQLite.*  
> *- Assegurar que combinações desastrosas (como solo arenoso + seca severa) aumentem o risco e tecnologias (irrigado) mitiguem o risco."*

### Resumo da Resposta da IA:
A IA desenvolveu o script `gerar_dataset.py`, calibrando uma função logística ($p = \frac{1}{1 + e^{-z}}$) com pesos ponderados para cada categoria e interações sinérgicas. O script gerou a base de treinamento gravada em `safra_treinamento.csv`, `safra_treinamento.sql` e `safra_treinamento.db`. Em refinamento posterior solicitado para testes em escala massiva de Big Data, o volume foi expandido para **200.000 registros**, apresentando distribuição estável de **19,2% de perdas (38.485 amostras)** e **80,8% de safras regulares (161.515 amostras)** com índices de busca B-Tree em todas as variáveis, refletindo com precisão atuarial as frequências do agronegócio nacional.

---

## Prompt 3 — Implementação do Classificador em SQL Puro (Etapa 3)

### Prompt enviado à IA:
> *"Agora preciso implementar o Classificador Naive Bayes diretamente na linguagem SQL, conforme exigido na Etapa 3 do PDF.*  
> *O algoritmo em SQL deve conter obrigatoriamente:*  
> *1. Cálculo das probabilidades a priori P(classe);*  
> *2. Cálculo das verossimilhanças P(feature = valor | classe) com suavização de Laplace (+1 e +|V|);*  
> *3. Classificação usando log-probabilidades (LN) para evitar underflow numérico;*  
> *4. Normalização do score final em probabilidade percentual (0% a 100%) usando função de janela (Softmax);*  
> *5. Saída com a probabilidade de cada classe e uma recomendação de decisão prática.*  
> *O código deve ser limpo, muito bem comentado e preparado para receber parâmetros dinâmicos (:v_tipo_solo, :v_seca, etc.)."*

### Resumo da Resposta da IA:
A IA gerou o arquivo `02_classificador_bayesiano.sql` estruturado em CTEs encadeadas (`WITH novo_caso`, `estatisticas_base`, `priori`, `verossimilhanca`, `score_bruto` e `SELECT` final com normalização por `SUM(score_exp) OVER()`). Além disso, desenvolveu o script `executar_testes.py` para rodar os testes automaticamente no SQLite.

---

## Prompt 4 — Análise dos Resultados e Reflexão Crítica (Etapas 4 e 5)

### Prompt enviado à IA:
> *"Criamos 5 cenários agrícolas de teste: baixo risco, alto risco extremo, dilema da irrigação, resiliência do solo argiloso e um caso inédito para testar Laplace.*  
> *Ajude-me a responder às perguntas da Etapa 4 e redigir a reflexão crítica:*  
> *1. O modelo classificou corretamente conforme a intuição agronômica?*  
> *2. Quais features tiveram maior log-odds (maior poder discriminativo)?*  
> *3. O que acontece quando testamos um solo nunca visto no treinamento?*  
> *4. Quais são as limitações da hipótese de independência condicional do Naive Bayes na agricultura?"*

### Resumo da Resposta da IA:
A IA calculou os rankings de log-odds (destacando `seca` e `irrigacao` como os maiores separadores de classe), comprovou o funcionamento da suavização de Laplace para categorias OOD (sem divisões por zero) e formulou a análise crítica sobre como a premissa "ingênua" do Naive Bayes ignora sinergias biológicas (como solo arenoso multiplicando o efeito da seca), embora funcione de maneira excelente como ferramenta de triagem prévia de risco e crédito.
