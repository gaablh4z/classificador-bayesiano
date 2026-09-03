# Relatório de Modelagem — Classificador Bayesiano de Atrasos em Entregas

**Nome do(s) aluno(s):** Gabriel Lemos Gomes e Lucas Peres de Lima
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

