# Frente 1 — Formação (Extensão vs. Poli): resumo para o relatório

Base: 187 respondentes da Poli, todos participantes de grupos de extensão. α = 0,05, testes bilaterais e correção de Holm sobre os 11 testes primários. A análise completa, com premissas, robustez e código, está em `notebooks/01_Formacao_Extensao_vs_Poli.ipynb`. As figuras ficam em `output/figures/frente1/` e as tabelas em `output/tables/frente1/`.

## Cuidados que valem para todos os resultados

- **Sem grupo de comparação:** os resultados são **percepções entre participantes**, não efeitos causais da extensão.
- **Efeito teto:** 64% deram nota 5 ao preparo na extensão, e ninguém deu 1 ou 2.
- **O ganho líquido é dominado pela nota das disciplinas** (ρ = −0,88). Por isso, toda diferença de ganho foi decomposta nas duas componentes.
- **Categoria do grupo e área do curso estão confundidas:** os grupos de Engenharia não têm alunos de Civil nem de Produção. Os resultados foram checados com estratificação e modelos.

## Tabela-resumo dos testes primários

| Pergunta | Teste | Estatística | p | p Holm | Efeito | Conclusão |
|---|---|---|---|---|---|---|
| P1 Extensão > disciplinas? | Wilcoxon pareado | W = 18 | 7 × 10⁻³¹ | < 10⁻²⁹ | r_rb = 0,998; d_z = 1,95 | **Sim**, quase unânime |
| P2 Ganho varia por área? | Kruskal-Wallis | H(4) = 9,66 | 0,047 | 0,19 | ε² = 0,05 | **Não** após Holm; perde significância com controle por categoria |
| P3 Ganho varia por categoria? | Kruskal-Wallis | H(3) = 22,48 | 5 × 10⁻⁵ | 3 × 10⁻⁴ | ε² = 0,12 | **Sim**, acompanhando as disciplinas |
| P3 Preparo na extensão varia por categoria? | Kruskal-Wallis | H(3) = 5,64 | 0,13 | 0,26 | ε² = 0,03 | **Não significativo** |
| P4a Horas × preparo na extensão | τ-b de Kendall | τ = 0,32 | 6 × 10⁻⁷ | 5 × 10⁻⁶ | τ = 0,32 | **Sim**, associação dose-resposta |
| P4b Tempo de grupo × preparo na extensão | τ-b de Kendall | τ = 0,07 | 0,29 | 0,29 | τ = 0,07 | **Não significativo** |
| P5 Preparo na extensão × importância da média | τ-b de Kendall | τ = −0,12 | 0,069 | 0,21 | τ = −0,12 | **Não significativo** |
| P6a Objetivo × importância da média | Kruskal-Wallis | H(4) = 48,55 | 7 × 10⁻¹⁰ | 7 × 10⁻⁹ | ε² = 0,27 | **Sim**, efeito grande |
| P6b Objetivo × preparo nas disciplinas | Kruskal-Wallis | H(4) = 16,50 | 0,0024 | 0,012 | ε² = 0,09 | **Sim** |
| P7a Modelo: horas → nota 5 na extensão | LR (logit) | LR(1) = 24,0 | 9 × 10⁻⁷ | 7 × 10⁻⁶ | OR = 1,93/faixa; AUC (CV) = 0,71 | **Sim**, poder moderado |
| P8 Modelo: objetivo → importância da média | LR (logit ordinal) | LR(4) = 65,8 | 2 × 10⁻¹³ | 2 × 10⁻¹² | R² de McFadden = 0,14 | **Sim**, previsão individual fraca |

## Conclusões prontas para a Seção 4

**P1 — Extensão × disciplinas (Figura 1).** Os participantes de grupos de extensão percebem um preparo profissional muito maior na extensão do que nas disciplinas obrigatórias: mediana 5 contra 2, diferença média de 2,3 pontos (IC 95%: 2,1 a 2,4; Wilcoxon p < 10⁻³⁰; r_rb ≈ 1). A percepção é quase unânime (93% favorecem a extensão e 0,5% as disciplinas) e se repete em todas as áreas de curso e categorias de grupo. Como é uma autoavaliação feita só por participantes, o resultado mede percepção relativa, e não um efeito causal da extensão.

**P2 + P3 — Áreas e categorias (Figuras 4 e 5).** O ganho da extensão sobre a grade aparece em todas as grandes áreas. As diferenças entre áreas são pequenas e perdem significância com a correção de Holm e com o controle da categoria do grupo. Entre categorias, o ganho é cerca de 1 ponto menor em grupos técnicos (Thunder Ratz, Poli Racing) do que em Consultoria & Negócios (1,6 contra 2,6; ε² = 0,12). A diferença não está no preparo percebido na extensão, alto em todas as categorias e sem diferença significativa (p = 0,13). Está na avaliação das disciplinas (2,9 contra 2,1), e se mantém entre alunos da mesma grande área. Uma hipótese plausível, não testada, é a complementaridade entre a grade e os projetos técnicos.

**P4 — Dedicação (Figuras 6 e 7).** O preparo percebido na extensão está associado à dedicação semanal: acima de 20 h por semana, 85% dão nota máxima, contra 38% de quem dedica até 5 h (τ-b = 0,32; p < 0,001). A associação também aparece dentro das categorias com amostra suficiente. O tempo de permanência no grupo não mostrou associação significativa (τ-b = 0,07; p = 0,29). Não há evidência de saturação, e o aparente platô acima de 20 h coincide com o teto da escala. A direção causal é indeterminada.

**P5 — Preparo na extensão × importância da média (Figura 8).** Não há evidência de que quem percebe mais preparo na extensão dê menos importância à média (τ-b = −0,12; p = 0,07), nem quando se controlam o objetivo atual e o preparo nas disciplinas. O que se associa à importância da média é a avaliação das disciplinas (τ-b = 0,22; p < 0,001).

**P6 — Objetivo atual (Figura 9).** O objetivo atual é o fator mais fortemente associado à importância dada à média (ε² = 0,27). Quem mira intercâmbio (média 3,9) ou IC (3,8) não difere significativamente de quem declara o desempenho acadêmico como objetivo (3,5), e valoriza a média bem mais do que quem foca no grupo (2,5) ou no estágio (2,6). Isso é coerente com seleções de intercâmbio e IC que usam a média. Quem prioriza o desempenho acadêmico também avalia melhor as disciplinas do que quem foca no estágio ou no grupo (3,0 contra 2,1–2,2).

**P7 — Modelo do preparo (Figura 10).** A dedicação semanal é o único preditor relevante da nota máxima de preparo na extensão: cada faixa de horas a mais praticamente dobra a chance (OR = 1,93; IC 95%: 1,45 a 2,55; 1,96 quando ajustado por tempo e categoria). O poder discriminante fora da amostra é moderado (AUC = 0,71 na validação cruzada), e categoria e tempo de grupo não acrescentam informação. O ganho líquido é explicado em 15% a 20% por horas (+0,32 por faixa) e grupo técnico (−0,63); pela decomposição, esta última diferença acompanha a avaliação das disciplinas.

**P8 — Modelo da importância da média (Figura 11, opcional).** A importância da média está fortemente associada ao objetivo atual: em relação a quem foca no grupo, a chance de dar mais importância à média é cerca de 33 vezes maior para quem mira intercâmbio (IC 95%: 11 a 99), 16 vezes para IC e 10 vezes para desempenho acadêmico. A área do curso não contribui. O modelo explica uma parcela modesta (R² de McFadden = 0,14) e é fraco para prever casos individuais: acurácia de 45% contra 40% de um palpite constante.

## Recomendação de corte

- **Manter no corpo do relatório:** P1, P3 (absorvendo a P2 como controle), P4, P6 e o modelo P7.
- **Citar em uma linha:** P5 (resultado nulo).
- **Apêndice ou opcional:** P8, que repete a P6 em forma de modelo.

## Limitações para a seção de discussão

- **Desenho e amostra:**
  - não há grupo de não participantes;
  - a amostra é de conveniência e dominada pela Poli Júnior (40%);
  - há viés de seleção e de sobrevivência.
- **Medida:**
  - autoavaliação de item único, com possível viés de método comum e de desejabilidade social;
  - efeito teto no preparo da extensão;
  - o ganho líquido trata a escala ordinal como intervalar;
  - os escores das faixas supõem espaçamento igual entre elas.
- **Grupos pequenos:** Empreendedorismo (n = 8) e IC / Pesquisa (n = 6) têm estimativas instáveis.
- **Inferência:**
  - o desenho é transversal;
  - as análises exploratórias não foram corrigidas por multiplicidade.

## Para o grupo

- O `anos_de_poli` do `clean_data.parquet` está errado em 30 linhas (bug no notebook 00). Isso afeta as Frentes 2 e 3. A correção está descrita em `.changelog/20261124-frente-1-formacao.md`.
- Achado exploratório que pode servir à Frente 3: a turma de ingresso se associa ao preparo percebido na extensão (80% de notas 5 na turma de 2024, contra 45% na de 2026), e o tempo de grupo não mostra associação consistente dentro das turmas.
