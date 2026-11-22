# Estudo sobre grupos de extensão da Poli

Este repositório centraliza os dados, o pré-processamento, as análises estatísticas e os resultados do estudo sobre grupos de extensão da Poli.

## Stack e execução

O projeto utiliza Python 3.12 e [uv](https://docs.astral.sh/uv/) para gerenciar o ambiente e as dependências.

Para preparar o ambiente:

```bash
uv sync
```

Para iniciar o Jupyter ou executar os notebooks:

```bash
uv run jupyter notebook
```

As dependências principais ficam declaradas em `pyproject.toml`, e a versão do Python usada pelo projeto fica registrada em `.python-version`.

## Estrutura de pastas

```text
.
|-- .changelog/          # registros históricos das decisões e trabalhos realizados
|-- data/                # dados brutos e processados
|-- notebooks/           # notebooks numerados e organizados por etapa
|-- output/
|   |-- figures/         # imagens e gráficos gerados
|   `-- tables/          # tabelas e resultados exportados
|-- src/
|   |-- plotting/        # funções reutilizáveis para visualização
|   `-- preprocessing.py # transformações e funções estatísticas compartilhadas
|-- pyproject.toml       # configuração do projeto e dependências
|-- uv.lock              # lockfile reproduzível do ambiente
`-- README.md
```

### Pastas de dados e resultados

- `data/raw_data.csv`: arquivo bruto recebido da coleta, considerado a fonte original.
- `data/clean_data.parquet`: conjunto tratado e utilizado pelas análises subsequentes.
- `output/tables/`: resultados tabulares exportados, normalmente em CSV.
- `output/figures/`: figuras geradas pelos notebooks.
- `.changelog/`: histórico de contexto para futuras sessões e alinhamento entre membros da equipe.

Os arquivos em `data/` são ignorados pelo Git conforme `.gitignore`, exceto quando houver necessidade explícita de versionar um conjunto pequeno e não sensível.

Não edite os dados brutos diretamente. Mudanças devem ser feitas por meio dos notebooks ou das funções em `src/`, e o resultado deve ser salvo como um novo arquivo tratado.

## Idioma

Adotamos o seguinte critério de idioma:

- **Código em EN-US**:
  - nomes de variáveis, funções, métodos, classes e módulos;
  - mensagens de erro destinadas a desenvolvedores;
  - comentários de código;
  - nomes de colunas intermediárias ou derivados criados pela programação.
- **Texto em PT-BR**:
  - README;
  - markdown e explicações dos notebooks;
  - títulos de gráficos, tabelas e documentos;
  - mensagens apresentadas ao usuário;
  - changelogs e demais documentos de contexto.

Valores e categorias que representam exatamente respostas coletadas no questionário devem permanecer em PT-BR, pois são parte do domínio dos dados. Nomes de APIs, bibliotecas e conceitos estatísticos podem manter a terminologia técnica original.

## Convenções de formato

### Notebooks

- Numere os notebooks em ordem de execução, usando dois dígitos: `00`, `01`, `02`, etc.
- Use nomes descritivos em Pascal Case com underscores separando palavras, por exemplo:

```text
00_Data_Processing.ipynb
01_Exploratory_Analysis.ipynb
02_Association_Tests.ipynb
```

- O número indica a etapa principal; o nome deve ser curto e refletir o objetivo do notebook.
- Exporte apenas resultados reutilizáveis para `output/` ou `data/`; não transforme o notebook em uma planilha ou armazenador permanente de dados intermediários.
- Execute os notebooks a partir da raiz do projeto para que caminhos relativos como `data/` e `output/` funcionem corretamente.

### Arquivos Python

- Módulos e scripts: `snake_case.py`.
- Funções e variáveis: `snake_case`.
- Constantes: `UPPER_SNAKE_CASE` ou `snake_case`.
- Classes: `PascalCase`.
- Utilize nomes em EN-US e evite abreviações ambíguas.
- Evite nomes genéricos como `df2`, `temp` ou `resultado_final` em novas interfaces reutilizáveis.

Exemplos:

```python
def convert_responses(df_renamed: pd.DataFrame, exclude_non_poli: bool = False) -> pd.DataFrame: ...


DEFAULT_ALPHA = 0.05
```

### Dados

- Use nomes de arquivos em snake case, sem espaços ou acentos.
- Preserve o nome de fonte bruta sem reescrita manual:
  - `raw_data.csv`;
  - `clean_data.parquet`.
- Novos conjuntos derivados devem indicar a transformação realizada, por exemplo:
  - `sample_without_missing_values.parquet`;
  - `association_test_results.csv`.
- Prefira Parquet para dados tabulares tratados que precisam preservar tipos, categorias e ordenações.
- Use CSV apenas quando houver necessidade de leitura por pessoas ou interoperabilidade com ferramentas externas.

### Figuras e tabelas

- Coloque figuras em `output/figures/`.
- Coloque tabelas exportáveis em `output/tables/`.
- Use nomes descritivos em snake case, por exemplo:
  - `observed_vs_expected_values.png`;
  - `adhesion_test.csv`.
- Após gerar artefatos, verifique se o notebook ou o script registra a interpretação deles em PT-BR.

### Changelog

- O repositório utiliza um changelog incremental em `.changelog/`.
- Nomeie cada arquivo com data e identificador curto:

```text
YYYYMMDD-short-description.md
```

Exemplo:

```text
20261121-preprocessing-pipeline.md
```

- Use PT-BR.
- Descreva o que foi feito, quais decisões foram tomadas, quais artefatos foram gerados e quais pontos não podem ser confundidos ou reutilizados sem cautela.
- Inclua dados ausentes, exclusões, hipóteses, resultados e limitações relevantes.
- Novos registros devem representar a mudança completa da sessão; não reescreva registros anteriores.

## Fluxo de trabalho

1. Trabalhe a partir dos dados limpos em `data/clean_data.parquet`.
2. Use ou estenda funções reutilizáveis em `src/` quando a transformação puder ser aplicada em mais de um notebook.
3. Preserve a ordem numerada dos notebooks e mantenha as etapas reproduzíveis.
4. Gere apenas os artefatos necessários em `data/` e `output/`.
5. Documente decisões relevantes em `.changelog/`.
6. Antes de concluir uma mudança, execute o menor conjunto de células ou testes capaz de validar o resultado afetado.