# Relatório de Modelagem — Classificador Bayesiano de Risco Agrícola

**Disciplina:** Mineração de Dados  
**Domínio Escolhido:** Agronegócio (Previsão de Quebra de Safra e Seguro Agrícola)  
**Participantes:** Lucas Peres de Lima, Gabriel Lemos Gomes  
**Entregável:** Etapa 1 do Roteiro da Atividade Prática 1  

---

## 1.1 Domínio e Contexto do Problema

O agronegócio de grãos (soja e milho) no Centro-Oeste brasileiro opera em escala massiva, porém exposto a severos riscos edafoclimáticos. Instituições financeiras, cooperativas de crédito e seguradoras agrícolas (operadoras de apólices rurais e PROAGRO) necessitam avaliar com precisão e agilidade o risco de sinistro antes da liberação de crédito de custeio e precificação de prêmios de seguro.

O objetivo do sistema é modelar o risco de insucesso de uma lavoura antes da colheita, permitindo a triagem proativa de centenas de milhares de contratos.

---

## 1.2 Rótulo Alvo (Variável Dependente)

A decisão binária a ser tomada é representada pelo atributo categórico:

$$\text{perda\_safra} \in \{\text{'sim'}, \text{'nao'}\}$$

A discretização da produtividade agrícola para a definição das classes do problema está detalhada na tabela a seguir:

| Rótulo Discreto (`perda_safra`) | Variável Contínua Subjacente | Faixa / Critério de Discretização | Classificação Operacional | Impacto Financeiro / Atuarial |
|---|---|---|---|---|
| **`sim`** | Produtividade colhida em relação à média histórica regional | Queda de rendimento $> 30\%$ (produtividade colhida $< 70\%$ da média histórica) | **Sinistro Ocorrido (Quebra de Safra)** | Acionamento da franquia de seguro agrícola / PROAGRO; quebra financeira; necessidade de renegociação do crédito de custeio. |
| **`nao`** | Produtividade colhida em relação à média histórica regional | Queda de rendimento $\le 30\%$ (produtividade colhida $\ge 70\%$ da média histórica) | **Safra Regular (Dentro da Meta Econômica)** | Faturamento operacional suficiente para cobrir custos de produção, liquidar financiamentos bancários e honrar contratos comerciais. |

---

## 1.3 As 7 Features Relevantes e Toda a Discretização em Tabela

Para garantir interpretabilidade, robustez algorítmica e conformidade com os parâmetros agronômicos oficiais do **ZARC (Zoneamento Agrícola de Risco Climático)** e da **Embrapa**, foram selecionadas 7 variáveis preditoras fundamentais. Cada variável contínua ou conceitual do campo foi discretizada em **3 categorias mutuamente exclusivas**, assegurando cardinalidade $|V_i| = 3$ uniforme (requisito para a calibração da Suavização de Laplace no Naive Bayes).

### Tabela Completa de Discretização das Variáveis Explicativas

| Feature (Atributo SQL) | Variável Contínua / Métrica Subjacente | Categoria Discretizada | Critério / Faixa de Discretização | Justificativa Agronômica no Domínio | Efeito no Risco de Perda |
|---|---|---|---|---|:---:|
| **`tipo_solo`** | Textura do solo e teor de argila na camada arável (0-20 cm) | `argiloso` | Teor de argila $> 35\%$ (ex.: Latossolo Vermelho / Argissolo) | Alta retenção de umidade e nutrientes na microporosidade; mantém disponibilidade hídrica por mais dias durante veranicos. | 🟢 **Reduz Risco** (Fator Protetor) |
| | | `medio` | Teor de argila entre $15\%$ e $35\%$ (textura média) | Equilíbrio entre retenção e aeração da raiz; capacidade intermediária de suporte hídrico. | 🟡 **Neutro / Moderado** |
| | | `arenoso` | Teor de argila $< 15\%$ (ex.: Neossolo Quartzarênico) | Baixa CTC e retenção hídrica insignificante; macroporosidade causa dessecação acelerada da rizosfera com poucos dias de sol. | 🔴 **Aumenta Risco** (Alta Vulnerabilidade) |
| **`seca`** | Dias consecutivos sem precipitação durante estádios críticos | `nenhuma` | $\le 7$ dias consecutivos de estiagem ao longo da safra | Turgor celular contínuo e fotossíntese plena; sem estresse osmótico que comprometa a floração. | 🟢 **Reduz Risco** (Cenário Ideal) |
| | | `moderada` | $8$ a $15$ dias consecutivos de estiagem | Estresse hídrico na fase vegetativa ou início de botões florais; desacelera o crescimento, mas com recuperação viável. | 🟡 **Neutro / Moderado** |
| | | `severa` | $> 15$ dias consecutivos sem chuva nos estádios R1 a R5 | Coincidência com floração e enchimento de grãos; causa abortamento massivo de vagens e chochamento irreversível. | 🔴 **Aumenta Risco** (Fator Crítico Máximo) |
| **`chuva`** | Volume pluviométrico acumulado ao longo de todo o ciclo da safra | `normal` | $1.200\text{ mm}$ a $1.800\text{ mm}$ bem distribuídos | Atende integralmente à evapotranspiração da cultura (ETc) da semeadura à maturação fisiológica. | 🟢 **Reduz Risco** (Ideal) |
| | | `excessiva` | $> 1.800\text{ mm}$ ou chuvas persistentes na maturação/colheita | Encharcamento, dificuldade de tráfego de colheitadeiras, umedecimento de vagens maduras e apodrecimento de grãos no pé ("grãos ardidos"). | 🟠 **Aumenta Risco** (Risco Operacional) |
| | | `pouca` | $< 1.000\text{ mm}$ de precipitação acumulada no ciclo | Déficit pluviométrico estrutural acumulado; diminuição de área foliar, biomassa e produtividade final. | 🔴 **Aumenta Risco** (Severo) |
| **`mes_plantio`** | Janela de semeadura em relação ao Zoneamento Agrícola (ZARC) | `outubro` | Semeadura entre 01 e 31 de outubro | Abertura recomendada; aproveita a maior radiação solar do verão e chuvas abundantes; assegura janela segura para a 2ª safra. | 🟢 **Reduz Risco** (Janela Ótima) |
| | | `novembro` | Semeadura entre 01 e 30 de novembro | Semeadura intermediária; condições de chuva favoráveis, porém encurta a margem operacional da cultura de safrinha. | 🟡 **Neutro / Aceitável** |
| | | `dezembro` | Semeadura após 01 de dezembro | Semeadura tardia de alto risco; fase de enchimento de grãos coincide com o declínio pluviométrico do outono e maior pressão de pragas. | 🔴 **Aumenta Risco** (Janela Tardia) |
| **`irrigacao`** | Tecnologia de manejo hídrico e cobertura protetora do solo | `irrigado` | Irrigação suplementar ativa por pivô central | Suprimento artificial automatizado de água; desacopla a lavoura das variações climáticas locais e mitiga estiagens. | 🟢 **Reduz Risco** (Máxima Blindagem) |
| | | `plantio_direto` | Cultivo em sequeiro com palhada densa e sem revolvimento | Palhada residual retém de 20% a 30% a mais de umidade no solo e atenua picos térmicos em relação ao manejo convencional. | 🟢 **Reduz Risco** (Manejo Conservacionista) |
| | | `convencional` | Cultivo em sequeiro com revolvimento mecânico (aração/grade) | Solo desnudo e desagregado; acelera a evaporação da água e expõe as raízes a altas temperaturas durante estiagens. | 🔴 **Aumenta Risco** (Vulnerável) |
| **`pragas`** | Severidade do ataque fitossanitário (percevejos, lagartas, fungos) | `baixa` | Infestação $< 10\%$ de desfolha ou abaixo do Nível de Dano Econômico (NDE) | Monitoramento rigoroso e controle biológico/químico eficaz; lavoura sem perda de área fotossintética funcional. | 🟢 **Reduz Risco** (Baixa Pressão) |
| | | `media` | Infestação entre $10\%$ e $30\%$ (limiar de controle econômico) | Populações sob controle com intervenções regulares; danos foliares pontuais sem destruição generalizada. | 🟡 **Neutro / Moderado** |
| | | `alta` | Infestação $> 30\%$ de desfolha ou escape de controle | Ataques descontrolados de percevejo-marrom (sucção de grãos) ou epidemia de ferrugem asiática (*Phakopsora pachyrhizi*). | 🔴 **Aumenta Risco** (Severo) |
| **`regiao`** | Macroambiente edafoclimático, altitude e relevo | `planalto` | Altitude $> 600\text{ m}$ (ex.: Chapadões dos Parecis e Médio-Norte) | Noites mais amenas que diminuem a respiração da planta, relevo plano apto à mecanização de precisão e solos profundos. | 🟢 **Reduz Risco** (Favorável) |
| | | `transicao` | Altitude entre $300\text{ m}$ e $600\text{ m}$ (relevo ondulado moderado) | Condições térmicas e pluviométricas medianas; aptidão agrícola regular. | 🟡 **Neutro** |
| | | `baixada` | Altitude $< 300\text{ m}$ (vales e depressões quentes) | Altas temperaturas constantes ($> 35^\circ\text{C}$), elevadíssima taxa de evapotranspiração e estresse térmico pronunciado. | 🔴 **Aumenta Risco** (Desfavorável) |

---

### Resumo das Variáveis e Parâmetros para o Classificador Bayesiano

A tabela abaixo consolida as especificações técnicas das variáveis no modelo, sua cardinalidade para a suavização de Laplace e os pesos calibrados no processo de modelagem:

| # | Coluna SQL | Tipo SQL | Variável Original / Conceitual | Categorias Discretizadas | Cardinalidade ($|V_i|$) | Impacto no Risco ($\beta_i$) |
|:---:|---|:---:|---|---|:---:|:---:|
| 1 | `tipo_solo` | `TEXT` | Teor de argila na análise de solo | `argiloso`, `medio`, `arenoso` | 3 | -1.2 / +0.1 / +1.4 |
| 2 | `seca` | `TEXT` | Dias consecutivos de veranico | `nenhuma`, `moderada`, `severa` | 3 | -1.6 / +0.1 / +2.4 |
| 3 | `chuva` | `TEXT` | Precipitação pluviométrica total (mm) | `normal`, `excessiva`, `pouca` | 3 | -1.3 / +0.5 / +1.8 |
| 4 | `mes_plantio` | `TEXT` | Data de semeadura (ZARC) | `outubro`, `novembro`, `dezembro` | 3 | -0.9 / +0.2 / +1.3 |
| 5 | `irrigacao` | `TEXT` | Sistema de cultivo e manejo hídrico | `plantio_direto`, `convencional`, `irrigado` | 3 | -0.5 / +1.0 / -2.0 |
| 6 | `pragas` | `TEXT` | Nível de infestação / dano foliar | `baixa`, `media`, `alta` | 3 | -1.0 / +0.1 / +1.6 |
| 7 | `regiao` | `TEXT` | Altitude e relevo (metros) | `planalto`, `transicao`, `baixada` | 3 | -0.7 / 0.0 / +0.8 |
| **Alvo** | `perda_safra` | `TEXT` | Queda de produtividade vs histórico | `nao`, `sim` | 2 | **Variável Dependente** |

---

## 1.4 Lógica Intuitiva por Trás dos Padrões de Risco

Na agricultura real, a perda de safra raramente decorre de um único fator isolado, mas sim do acúmulo de vulnerabilidades e da presença (ou ausência) de mitigações tecnológicas:

### Síntese Tabular dos Padrões de Risco e Interações

| Padrão / Arquétipo de Risco | Combinação Característica | Dinâmica Agronômica no Campo | Impacto na Decisão do Modelo |
|---|---|---|---|
| **Vulnerabilidade Estrutural Crítica** | `tipo_solo = 'arenoso'` + `seca = 'severa'` + `chuva = 'pouca'` | Ausência de microporosidade e reservatório hídrico subterrâneo somada à alta taxa de evapotranspiração; dessecação rápida e colapso celular da lavoura. | Probabilidade de perda superior a 90% (recusa de crédito / sinistro iminente). |
| **Mitigação Tecnológica Plena** | `irrigacao = 'irrigado'` + qualquer cenário de déficit pluviométrico | O pivô central supre de forma contínua a lâmina de água requerida, neutralizando quase integralmente a escassez de chuva. | Risco atenuado para patamares mínimos (< 5% de perda), viabilizando concessão de crédito. |
| **Exposição Fenológica Tardia** | `mes_plantio = 'dezembro'` + `pragas = 'alta'` | A fase reprodutiva crítica coincide com o fim das chuvas de verão e com o pico de infestação de percevejos e fungos. | Risco substancialmente elevado mesmo em solos férteis. |
| **Resiliência Edáfica Natural** | `tipo_solo = 'argiloso'` + `seca = 'moderada'` | A elevada microporosidade dos latossolos argilosos retém água capilar e amortece veranicos curtos sem comprometer a colheita. | Preserva a viabilidade produtiva com risco moderado e controlado (~30% a 35%). |

O modelo Naive Bayes analisa essas evidências calculando a probabilidade condicional de cada fator $P(\text{feature} \mid \text{perda\_safra})$ e multiplica essas probabilidades acumuladas (na escala logarítmica) para estimar a probabilidade a posteriori de perda.
