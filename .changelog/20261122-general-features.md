# 20261122 - Criacao de features gerais

## Objetivo

Registrar as variaveis derivadas adicionadas ao notebook `notebooks/00_Data_Processing.ipynb`. Sao features consideradas suficientemente gerais para fazer parte do pre-processamento atual; isso nao significa que toda feature futura deva ser criada nessa etapa.

## Features adicionadas

- `categoria_extensao`: agrupa `grupo_extensao` em categorias mais amplas:
  - `Poli Júnior`, `Grupo de Negócios da Poli` e `Poli Consulting Club` -> `Consultoria & Negócios`;
  - `Poli Quant`, `Poli Real State` e `Poli Finance` -> `Mercado Financeiro`;
  - `Thunder Ratz` e `Poli Racing` -> `Engenharia`;
  - `Liga de Empreendedorismo da Poli` -> `Empreendedorismo`;
  - grupos sem correspondencia no mapeamento -> `Outros`.
- `anos_de_poli`: calcula o tempo desde o ingresso como `2026 - ano_ingresso + 1`. O resultado depende do ano de referencia usado no notebook.
- `qtd_outras_atividades`: soma as flags `extra_esportes`, `extra_ca_gremio` e `extra_outro_grupo`, contando em quantas dessas atividades a pessoa participa, alem do grupo principal.

As novas colunas sao criadas em `df_clean` durante a execucao do notebook.

## Escopo para features futuras

As variaveis acima foram consideradas de carater mais geral para a base atual. Outras features que possam ser uteis devem ser estudadas caso a caso nos proximos notebooks, considerando a pergunta de pesquisa, os dados disponiveis e a interpretacao estatistica. Nao se deve presumir que essas features adicionais sejam universais ou devam ser incorporadas ao pre-processamento compartilhado.

O agrupamento de grupos de extensao tambem reflete uma decisao analitica para esta pesquisa e deve ser revisto se os grupos ou o objetivo da analise mudarem.
