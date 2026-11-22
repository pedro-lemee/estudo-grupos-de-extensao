# 20261121 - Pre-processamento dos dados da pesquisa

## Objetivo

Documentar o estado produzido pelo notebook `notebooks/00_Data_Processing.ipynb`, incluindo as transformacoes aplicadas, os artefatos gerados e os cuidados que devem ser considerados por futuras sessoes e pelos demais membros da equipe.

## Dados de entrada e saida

- Fonte: `data/raw_data.csv`.
- Saida principal: `data/clean_data.parquet`.
- O Parquet foi escolhido para preservar os metadados das colunas categorizadas, especialmente suas categorias e a ordenacao.
- Resultado: 187 observacoes e 24 colunas no conjunto limpo.
- Foram removidos os registros cujo curso era `Não faço Poli`; a limpeza foi feita por `exclude_non_poli=True` em `convert_responses`.
- O conjunto limpo nao inclui os registros que responderam fora da Poli. Qualquer analise que precise contemplar o publico externo deve ser feita partindo de `df_renamed` ou executando o pre-processamento sem essa exclusao.

## Renomeacao e limpeza das colunas

- As perguntas do CSV foram renomeadas para nomes de variaveis sem texto de pergunta, conforme a lista `cols_names` do notebook.
- `timestamp` foi convertido para `datetime` com o formato `dd/mm/YYYY HH:MM:SS`.
- `termo_consentimento` foi removido apos o uso da renomeacao porque nao representa uma resposta analitica.
- Espacos nas extremidades das respostas textuais foram removidos.
- As seguintes variaveis foram configuradas como categorizadas nominais: `curso`, `tipo_escola`, `area_pretendida`, `grupo_extensao`, `motivacao_ingresso`, `faz_atividade_remunerada` e `objetivo_faculdade`.
- As seguintes variaveis ordinais foram preservadas com suas categorias em ordem logica:
  - `tempo_deslocamento`;
  - `renda_familiar`;
  - `media_ponderada`;
  - `tempo_grupo`;
  - `horas_semanais_grupo`;
  - `momento_estagio`.

## Variaveis de escolha multipla

- `outras_extracurriculares` permitia mais de uma resposta e foi transformada em tres flags booleanas:
  - `extra_esportes`;
  - `extra_outro_grupo`;
  - `extra_ca_gremio`.
- A coluna original `outras_extracurriculares` foi removida.
- Essas flags podem ser usadas para indicar a presenca de cada alternativa, mas nao representam a exclusividade da categoria.

## Padronizacao manual

### `objetivo_faculdade`

- Respostas livres ou nao padronizadas foram revisadas.
- Seis respostas semelhantes a categorias existentes foram incorporadas a elas por meio de um mapeamento:
  - `Foco no grupo de extensão` -> `Grupo de extensão`;
  - `Busca e realização de estágio` -> `Estágio`;
  - `Desempenho acadêmico (manter/elevar a média ponderada)` -> `Desempenho acadêmico`;
  - `Planejamento e realização de intercâmbio` -> `Intercâmbio`;
  - `Iniciação científica / Pesquisa acadêmica` -> `IC / Pesquisa`;
  - `Estou atualmente em intercâmbio (...)` -> `Intercâmbio`.
- Respostas personalizadas restantes foram substituidas por `NaN`.
- Decisao importante: nao foram criadas flags booleanas, porque isso contrariaria a metodologia de escolha unica adotada no formulario. Tampouco foi criada uma categoria generica `outros`, pois a equipe considerou que a maioria dessas respostas ja representava combinacoes de categorias existentes e que uma categoria agregada esconderia essa natureza. Foram 7 observacoes afetadas por essa conversao.

### `faz_atividade_remunerada`

Os textos longos do formulario foram reduzidos para tres categorias ordinais:

- `Não`;
- `Parcial / pontual`;
- `Recorrente / contínuo`.

## Valores ausentes

Apos o pre-processamento, os valores ausentes conhecidos sao:

- `renda_familiar`: 24;
- `media_ponderada`: 3;
- `objetivo_faculdade`: 7.

Os dois primeiros casos sao majoritariamente associados a respostas como `Prefiro não informar`. Os 7 ausentes de `objetivo_faculdade` correspondem a respostas personalizadas que nao puderam ser agregadas com seguranca.

O notebook nao define uma imputacao global. A decisao sobre excluir, imputar ou codificar `NaN` deve ser tomada separadamente em cada analise, conforme a pergunta estatistica e o tamanho da base apos a filtragem.

## Aproximacao continua de variaveis intervalares

Tres variaveis foram consideradas candidatas a aproximacao continua: `tempo_deslocamento`, `media_ponderada` e `horas_semanais_grupo`. `tempo_grupo` nao foi aproximado por ser comparavel apenas dentro dos ciclos reais de cada grupo, que podem ter duracoes e periodos diferentes.

### Metodo

- As frequencias foram ajustadas por `binned MLE` usando `scipy.optimize.minimize`.
- O algoritmo implementado em `src/preprocessing.py` maximiza a log-verossimilhanca multinomial para dados agrupados em intervalos.
- O ajuste das distribuições foi avaliado por teste Qui-quadrado de aderencia com `alpha = 0.05`.
- Distribuicoes consideradas com base na inspeção visual:
  - `tempo_deslocamento`: Lognormal;
  - `media_ponderada`: Normal;
  - `horas_semanais_grupo`: Lognormal.

O ajuste usa os seguintes limites:

- Tempo de deslocamento: 0, 30, 60, 120 e infinito.
- Media ponderada: menos infinito, 5, 6, 7, 8, 9 e infinito.
- Horas semanais: 0, 5, 10, 20, 40 e infinito.

### Resultados do teste de aderencia

Os resultados, preservados em `output/tables/adhesion_test.csv`, foram:

| Variavel | Distribuicao | Parametros | Chi-quadrado | Critico | DoF | p-valor | Resultado |
|---|---|---:|---:|---:|---:|---:|---|
| Tempo Deslocamento | Lognormal | mu_ln=3.6701, sigma_ln=0.6822 | 0.1058 | 3.8415 | 1 | 0.7450 | Falha em rejeitar H0 |
| Media Ponderada | Normal | mu=7.2219, sigma=1.0254 | 2.2267 | 7.8147 | 3 | 0.5267 | Falha em rejeitar H0 |
| Horas Semanais Grupo | Lognormal | mu_ln=2.7118, sigma_ln=0.9146 | 1.2998 | 5.9915 | 2 | 0.5221 | Falha em rejeitar H0 |

O grafico de observados versus esperados foi salvo em `output/figures/observed_vs_expected_values.png`.

## Conversao para valores continuos aproximados

Cada faixa categorizada foi substituida pelo valor esperado condicional dentro do intervalo segundo a distribuicao ajustada:

`E[X | intervalo]`

As novas colunas criadas foram:

- `tempo_deslocamento_num`;
- `media_ponderada_num`;
- `horas_semanais_grupo_num`.

Os valores foram arredondados para duas casas decimais.

Exemplos dos resultados esperados incluem a substituicao das faixas de tempo por valores aproximados, como 20.13, 42.98, 81.18 e o valor correspondente ao ultimo intervalo aberto. Os valores exatos sao determinados pela distribucao ajustada e podem ser consultados no Parquet limpo.

## Pontos de atencao e limites

- Esta aproximacao nao recupera os valores individuais reais coletados no formulario.
- Os testes estatisticos nao devem ser aplicados diretamente em `*_num` como se fossem dados brutos, pois os valores foram sintetizados a partir de intervalos e carregam incerteza intrinseca.
- Um criterio mais rigoroso deve ser adotado em qualquer inferencia baseada nessas variaveis aproximadas.
- Essas colunas podem ser uteis para analise descritiva, visualizacao e modelagem em que uma representacao continua seja necessaria, mas nao substituem a leitura cautelosa das categorias originais.
- `tempo_grupo` nao deve ser aproximado para continuidade sem um estudo adicional.
- Toda analise deve declarar explicitamente como tratou os `NaN`.
- Os valores aproximados nao devem ser usados para afirmar precisao individual ou como medidas oficiais dos participantes.
- O ajuste Binned MLE e o teste Qui-quadrado nao possuem correcoes adicionais para a incerteza de estimacao dos parametros; isso nao foi incorporado no teste atual.
- Os arquivos gerados dependem da ordem e da escrita da pesquisa. Mudancas no CSV bruto podem invalidar nomes, categorias, ordens ou contagens e exigem nova execucao.

## Funcoes auxiliares relevantes

As implementacoes compartilhadas ficam em `src/preprocessing.py`:

- `convert_responses`: limpeza, categorizacao, exclusao de nao-Poli e expansao das atividades extracurriculares;
- `fit_binned_mle`: ajuste numerico da verossimilhança agrupada;
- `chi_square_gof`: teste Qui-quadrado de aderencia;
- `compute_bin_expected_values`: calculo do valor esperado condicional de cada faixa.

## Como continuar

Para reproduzir o pre-processamento:

1. Abra `notebooks/00_Data_Processing.ipynb`.
2. Garanta que o ambiente do projeto esteja ativo.
3. Execute as celulas na ordem.
4. Confirme que `data/clean_data.parquet`, `output/tables/adhesion_test.csv` e `output/figures/observed_vs_expected_values.png` foram atualizados.

Mudancas futuras devem ser registradas em um novo arquivo dentro de `.changelog/`, com data no formato `YYYYMMDD` e um identificador curto.