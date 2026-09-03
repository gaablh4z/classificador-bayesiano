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

