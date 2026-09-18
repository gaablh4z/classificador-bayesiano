# Contexto do Projeto — Classificador Naive Bayes em Larga Escala (Agronegócio MT)

> Documento de contexto para geração assistida por IA (Antigravity). Contém toda a especificação técnica, funcional e matemática necessária para implementar o projeto do zero.

## 1. Objetivo do Projeto

Construir uma ferramenta analítica de alta performance em **Rust + Apache Polars** que implementa, "na mão" (sem bibliotecas de ML prontas), um classificador probabilístico **Naive Bayes** para prever risco de **quebra de safra** em talhões agrícolas de Mato Grosso, processando um dataset sintético de **500.000 registros** de forma vetorizada, multithread e memory-safe.

**Rótulo alvo (classificação binária):**
- `quebra_safra = 'sim'` → produtividade < 70% da média histórica (aciona sinistro/seguro agrícola)
- `quebra_safra = 'nao'` → safra dentro da meta econômica regional

## 2. Stack Técnica

- **Linguagem:** Rust
- **Processamento de dados:** Apache Polars (DataFrames vetorizados, multithread)
- **Geração do dataset:** Python (script auxiliar, não faz parte do pipeline de inferência)
- **Sem** bibliotecas de Machine Learning prontas — toda a matemática do Naive Bayes (priors, verossimilhança, suavização de Laplace, log-odds, softmax) deve ser implementada manualmente em `bayes.rs`

## 3. Estrutura de Pastas e Arquivos a Gerar

```
naive_bayes_agro_mt/
├── Cargo.toml                          # Manifesto e dependências de compilação em Rust
├── README.md                           # Instruções de reprodução, build e execução
│
├── docs/
│   ├── modelagem/
│   │   ├── definicao_problema.md       # Rótulo alvo, objetivos e justificativas regionais
│   │   └── dicionario_features.md      # As 7 variáveis calibradas com o ZARC/MT
│   ├── prompts/
│   │   └── historico_dialogo_ia.md     # Registro integral do diálogo e decisões com a IA
│   └── relatorio/
│       ├── analise_casos_teste.md      # Interpretação dos 5 cenários avaliados
│       └── reflexao_critica.md         # Análise de limitações perante a banca agronômica
│
├── scripts/
│   └── gerar_dataset_500k.py           # Script gerador da base sintética com regras de MT
│
├── dataset/
│   ├── treinamento_mt_500k.csv         # Base histórica com 500.000 registros
│   └── casos_teste.csv                 # Os 5 perfis de talhões para validação
│
└── src/
    ├── main.rs                         # Pipeline principal: carga, multithread, testes e métricas
    ├── bayes.rs                        # Matemática artesanal do Naive Bayes (Laplace, Log-odds)
    └── tipos.rs                        # Structs e tipos auxiliares
```

## 4. Dicionário de Features (calibradas com ZARC/MT)

Todas as 7 features são categóricas (discretizadas). Cada uma tem 3 categorias possíveis.

| Feature | Categorias | Fundamentação técnica / impacto regional em MT |
|---|---|---|
| `classe_pedologica` | `latossolo_argiloso`, `plintossolo_cerrado`, `neossolo_arenoso` | Latossolos profundos do Médio-Norte retêm água por mais tempo; Neossolos quartzarênicos (<15% argila) do Araguaia e Parecis colapsam em poucos dias de sol intenso. |
| `deficit_hidrico_estadio` | `sem_deficit_reprodutivo`, `moderado_vegetativo`, `severo_fase_r1_r5` | Estresse hídrico no enchimento de grãos (R1-R5) provoca chochamento e abortamento irreversível; na fase vegetativa a cultura é mais resiliente. |
| `regime_chuva` | `deficitario`, `regular_ideal`, `excessivo_colheita` | Déficit quebra o rendimento das vagens; chuva excessiva na colheita causa apodrecimento dos grãos no pé (grãos ardidos). |
| `janela_zarc` | `ideal_outubro`, `ajustada_novembro`, `tardia_dezembro` | Conforme o Zoneamento de Risco Climático da Embrapa, semeaduras em dezembro inviabilizam o milho 2ª safra e elevam a pressão de ferrugem. |
| `sistema_cultivo` | `sequeiro_convencional`, `sequeiro_plantio_direto`, `irrigado_pivo` | Plantio direto com palhada densa preserva umidade residual do solo; pivô central anula a dependência imediata do clima. |
| `pressao_fitossanitaria` | `baixa_preventiva`, `moderada_monitorada`, `critica_escape` | Controle integrado para ferrugem asiática (*Phakopsora pachyrhizi*), percevejo-marrom e nematóides de solos arenosos. |
| `microrregiao_altitude` | `chapadao_alta` (>600m), `depressao_cuiabana` (<300m), `transicao_media` | Chapadões (Diamantino, Campo Novo) têm noites mais amenas; baixadas sofrem calor constante e alta evapotranspiração. |

## 5. Formulação Matemática (implementar em `bayes.rs`)

**1. Probabilidade a priori (multithread, contagem paralela por classe):**

```
P(C) = Total(C) / N
ln(P(C)) = ln(P(C))
```

**2. Verossimilhança com suavização dinâmica de Laplace:**

```
P(xi | C) = [ Contagem(xi em C) + 1.0 ] / [ Total da classe C + |Vi| ]
```
onde `|Vi|` é o número dinâmico de categorias distintas da feature `i` (evita divisão por zero em categorias não vistas no treino).

**3. Soma em escala logarítmica (anti-underflow):**

```
Score(C) = ln(P(C)) + Σ (i=1 a 7) ln(P(xi | C))
```

**4. Normalização robusta (softmax bayesiano):**

```
P(sim) = e^(Score(sim) - max) / [ e^(Score(sim) - max) + e^(Score(nao) - max) ] × 100
```
A subtração do termo `max(Score(sim), Score(nao))` evita overflow numérico de ponto flutuante.

## 6. Casos de Teste (para `casos_teste.csv` e validação)

| # | Cenário | Perfil | Resultado esperado |
|---|---|---|---|
| 1 | Baixo risco — Chapadão dos Parecis | Latossolo argiloso, sem déficit em fase crítica, chuva regular, janela outubro, pivô central | Probabilidade de quebra < 5% |
| 2 | Alto risco extremo | Neossolo arenoso, seca severa em R1-R5, chuva deficitária, plantio em dezembro, sequeiro convencional | Probabilidade de quebra > 90% |
| 3 | Dilema edáfico | Neossolo arenoso sob pivô central com irrigação plena | Testa se a tecnologia compensa a fragilidade do solo arenoso |
| 4 | Resiliência da argila | Latossolo argiloso exposto a veranico severo e chuva deficitária | Mede o amortecimento da microporosidade do solo argiloso |
| 5 | Teste de Laplace | `classe_pedologica = 'gleissolo_desconhecido'` (categoria fora do treino) | Comprova que o código não quebra com categorias não vistas |

## 7. Requisitos Não-Funcionais

- Processar os 500.000 registros e classificar os 5 casos de teste em **menos de 0,5 segundo**.
- Uso de multithreading no carregamento e na contagem de classes/features (via Polars/Rayon).
- Segurança de memória nativa do Rust (sem unsafe desnecessário).

## 8. Limitações Conhecidas (documentar em `reflexao_critica.md`)

- O algoritmo assume **independência condicional** entre as variáveis — hipótese ecologicamente falsa no cerrado matogrossense: um solo arenoso multiplica catastroficamente o impacto da seca no enchimento de grãos, pois não possui reserva hídrica.
- O modelo soma os pesos das features isoladamente; deve ser interpretado como um **baseline probabilístico de crédito/triagem**, não como um simulador ecofisiológico de plantas.

## 9. Instruções para o Agente (Antigravity)

1. Gerar `scripts/gerar_dataset_500k.py`, que produz `dataset/treinamento_mt_500k.csv` com 500.000 linhas, respeitando as 7 features e regras de correlação implícitas na fundamentação técnica (ex.: neossolo arenoso + déficit severo em R1-R5 + chuva deficitária deve gerar viés forte para `quebra_safra = sim`).
2. Gerar `dataset/casos_teste.csv` com os 5 perfis descritos na Seção 6.
3. Implementar `src/tipos.rs` com as structs de dados (linha do dataset, contagens por classe/feature, resultado de classificação).
4. Implementar `src/bayes.rs` com as 4 etapas matemáticas da Seção 5, usando Polars para agregações vetorizadas/paralelas.
5. Implementar `src/main.rs`: carrega o CSV de treino, treina o modelo (contagens), roda os 5 casos de teste, imprime probabilidades e tempo de execução.
6. Gerar a documentação de apoio em `docs/` (modelagem, relatório dos casos de teste, reflexão crítica) alinhada às Seções 4, 6 e 8 deste documento.
7. Gerar `Cargo.toml` com as dependências (Polars, Rayon se necessário) e `README.md` com instruções de build (`cargo build --release`) e execução.
