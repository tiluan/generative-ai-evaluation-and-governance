# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">
# MAGIC </div>
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC # Avaliação de Benchmark
# MAGIC
# MAGIC
# MAGIC Nesta demonstração, **nos concentraremos na avaliação de large language models usando um dataset de referência específico para a tarefa em questão.**
# MAGIC
# MAGIC **Objetivos de Aprendizagem:**
# MAGIC
# MAGIC *Ao final desta demonstração, você será capaz de:*
# MAGIC
# MAGIC * Obter dataset de referência/benchmark para avaliação de LLM específico da tarefa
# MAGIC * Avaliar o desempenho de um LLM em uma tarefa específica usando métricas específicas da tarefa
# MAGIC * Comparar o desempenho relativo de dois LLMs usando um conjunto de referência

# COMMAND ----------

# MAGIC %md
# MAGIC ## Requisitos
# MAGIC
# MAGIC Por favor, revise os seguintes requisitos antes de iniciar a lição:
# MAGIC
# MAGIC * Para executar este Notebook, você precisa usar um dos seguintes tempos de execução do Databricks: **15.4.x-cpu-ml-scala2.12**
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ## Configuração da Sala de aula
# MAGIC
# MAGIC Instale as bibliotecas necessárias.

# COMMAND ----------

# MAGIC %pip install -U -qq databricks-sdk rouge_score evaluate textstat
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC Antes de começar a demonstração, execute o script de configuração de sala de aula fornecido. Esse script definirá as variáveis de configuração necessárias para a demonstração. Execute a seguinte célula:

# COMMAND ----------

# MAGIC %run ../Includes/Classroom-Setup-03

# COMMAND ----------

# MAGIC %md
# MAGIC **Outras Convenções:**
# MAGIC
# MAGIC Ao longo desta demonstração, faremos referência ao objeto `DA`. Esse objeto, fornecido pelo Databricks Academy, contém variáveis como seu nome de usuário, nome do catálogo, nome do esquema, diretório de trabalho e locais do conjunto de dados. Execute o bloco de código abaixo para visualizar esses detalhes:

# COMMAND ----------

print(f"Username:          {DA.username}")
print(f"Catalog Name:      {DA.catalog_name}")
print(f"Schema Name:       {DA.schema_name}")
print(f"Working Directory: {DA.paths.working_dir}")
print(f"Dataset Location:  {DA.paths.datasets}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Visão geral da demonstração
# MAGIC
# MAGIC Nesta demonstração, avaliaremos o desempenho de um sistema de IA projetado para resumir texto.
# MAGIC
# MAGIC Os documentos de texto que resumiremos são uma coleção de avaliações fictícias de produtos de supermercado.
# MAGIC
# MAGIC O sistema de IA funciona da seguinte forma:
# MAGIC
# MAGIC 1. Aceita um documento de texto como entrada
# MAGIC 2. Constrói um prompt de LLM usando aprendizado de poucos exemplos para resumir o texto
# MAGIC 3. Envia o estímulo a um LLM para resumo
# MAGIC 4. Retorna texto resumido
# MAGIC
# MAGIC Veja abaixo um exemplo do sistema.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo 1: Preparar modelos a serem usados
# MAGIC
# MAGIC A seguir, prepararemos o modelo que será utilizado para avaliação.
# MAGIC
# MAGIC Usaremos **Databricks Claude 3.7 Sonnet** e **Llama3-70b-chat** para avaliação.

# COMMAND ----------

from databricks.sdk.service.serving import ChatMessage
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Define the first model for summarization
def query_summary_system(input: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "You are an assistant that summarizes text. Given a text input, you need to provide a one-sentence summary. You specialize in summarizing reviews of grocery products. Please keep the reviews in first-person perspective if they're originally written in first person. Do not change the sentiment. Do not create a run-on sentence – be concise."
        },
        { 
            "role": "user", 
            "content": input 
        }
    ]
    messages = [ChatMessage.from_dict(message) for message in messages]
    chat_response = w.serving_endpoints.query(
        name="databricks-claude-3-7-sonnet",
        messages=messages,
        temperature=0.1,
        max_tokens=128
    )

    return chat_response.as_dict()["choices"][0]["message"]["content"]

# Define the second model for summarization
def challenger_query_summary_system(input: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "You are an assistant that summarizes text. Given a text input, you need to provide a one-sentence summary. You specialize in summarizing reviews of grocery products. Please keep the reviews in first-person perspective if they're originally written in first person. Do not change the sentiment. Do not create a run-on sentence – be concise."
        },
        { 
            "role": "user", 
            "content": input 
        }
    ]
    messages = [ChatMessage.from_dict(message) for message in messages]
    chat_response = w.serving_endpoints.query(
        name="databricks-meta-llama-3-3-70b-instruct",
        messages=messages,
        temperature=0.1,
        max_tokens=128
    )

    return chat_response.as_dict()["choices"][0]["message"]["content"]

# COMMAND ----------

# MAGIC %md
# MAGIC Vamos testar os modelos!

# COMMAND ----------

query_summary_system(
    "This is the best frozen pizza I've ever had! Sure, it's not the healthiest, but it tasted just like it was delivered from our favorite pizzeria down the street. The cheese browned nicely and fresh tomatoes are a nice touch, too! I would buy it again despite it's high price. If I could change one thing, I'd made it a little healthier – could we get a gluten-free crust option? My son would love that."
)

# COMMAND ----------

challenger_query_summary_system(
    "This is the best frozen pizza I've ever had! Sure, it's not the healthiest, but it tasted just like it was delivered from our favorite pizzeria down the street. The cheese browned nicely and fresh tomatoes are a nice touch, too! I would buy it again despite it's high price. If I could change one thing, I'd made it a little healthier – could we get a gluten-free crust option? My son would love that."
)

# COMMAND ----------

# MAGIC %md
# MAGIC Para concluir esse fluxo de trabalho, vamos nos concentrar nos seguintes passos:
# MAGIC
# MAGIC 1. Obter um conjunto de benchmark para avaliar a sumarização
# MAGIC 2. Calcular métricas de avaliação específicas de sumarização usando o conjunto de benchmark
# MAGIC 3. Compare o desempenho com outro LLM usando o conjunto de benchmark e as métricas de avaliação

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo 2: Benchmark e conjuntos de referência
# MAGIC
# MAGIC Como um lembrete, nossas métricas de avaliação específicas de tarefa (incluindo ROUGE para resumo) exigem um conjunto de benchmark para calcular pontuações.
# MAGIC
# MAGIC Existem dois tipos de conjuntos de referência/benchmark que podemos usar:
# MAGIC
# MAGIC 1. Conjuntos de benchmark grandes e genéricos comumente usados em casos de uso
# MAGIC 2. Conjuntos de benchmark específicos do domínio para o seu caso de uso
# MAGIC
# MAGIC Para esta demonstração, vamos nos concentrar na anterior.
# MAGIC
# MAGIC ### Conjunto de Benchmark Genérico
# MAGIC
# MAGIC Primeiro, importaremos um conjunto de benchmark genérico usado para avaliar o resumo de texto.
# MAGIC
# MAGIC Usaremos o dataset usado em [Benchmarking Large Language Models for News Summarization](https://arxiv.org/abs/2301.13848) para avaliar o quão bem nossa solução de LLM resume o texto comum.
# MAGIC
# MAGIC Este dataset:
# MAGIC
# MAGIC * é relativamente grande em escala com 599 entradas
# MAGIC * está relacionado com artigos de notícias
# MAGIC * contém texto original e resumos *escritos pelo autor* do texto original
# MAGIC
# MAGIC **Pergunta:** Qual é a vantagem de usar resumos de referência que são escritos pelo autor original?

# COMMAND ----------

import pandas as pd

# Leia e display the dataset
eval_data = pd.read_csv(f"{DA.paths.datasets.news}/csv/news-summaries.csv")
display(eval_data)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo 4: Calcular a métrica de avaliação do ROUGE
# MAGIC
# MAGIC Em seguida, desejaremos calcular nossa métrica ROUGE-N para entender quão bem nosso sistema resume o texto genérico de produtos de supermercado usando o dataset.
# MAGIC
# MAGIC Podemos calcular a métrica ROUGE (entre outras) usando os novos recursos de avaliação de LLM do MLflow. A avaliação do MLflow LLM inclui coleções default de métricas para tarefas pré-selecionadas, por exemplo, "resposta a perguntas" ou "resumo de texto" (nosso caso). Dependendo do caso de uso do LLM que você está avaliando, essas coleções predefinidas podem simplificar muito o processo de execução de avaliações.
# MAGIC
# MAGIC A função  `mlflow.evaluate` aceita os seguintes parâmetros para esse caso de uso:
# MAGIC
# MAGIC * Um modelo LLM
# MAGIC * Dados de referência para avaliação (nosso conjunto de benchmark)
# MAGIC * Coluna com dados de referência
# MAGIC * O modelo/tipo de tarefa (por exemplo `"text-summarization"`)
# MAGIC
# MAGIC **Nota:** O `text-summarization` tipo calculará automaticamente as métricas relacionadas ao ROUGE. Para algumas métricas, serão necessárias instalações de biblioteca adicionais – você pode ver os requisitos na saída impressa.

# COMMAND ----------

# A função personalizada para iterar através do nosso DF de avaliação
def query_iteration(inputs):
    answers = []

    for index, row in inputs.iterrows():
        completion = query_summary_system(row["inputs"])
        answers.append(completion)

    return answers

# Função de query_iteration de teste – ela precisa retornar uma lista de strings de saída
query_iteration(eval_data.head())

# COMMAND ----------

import mlflow

# `Evaluate` de MLflow com uma função personalizada
results = mlflow.evaluate(
    query_iteration,                      # função iterativa de cima
    eval_data.head(50),                   # limitando para velocidade
    targets="writer_summary",             # coluna com saída esperada ou "boa"
    model_type="text-summarization"       # tipo de modelo ou tarefa
)

# COMMAND ----------

# MAGIC %md
# MAGIC Podemos ver os resultados de registros individuais por subconjunto do objeto útil `.tables` .
# MAGIC
# MAGIC Observe todas as diferentes versões da métrica ROUGE. Essas métricas são calculadas usando a biblioteca HuggingFace `evaluator` e as métricas são detalhadas [aqui](https://huggingface.co/spaces/Remeris/rouge_ru).
# MAGIC
# MAGIC Em resumo, as descrições de cada métrica estão abaixo:
# MAGIC
# MAGIC * "rouge1": Pontuação baseada em unigrama (1-grama)
# MAGIC * "rouge2": Pontuação baseada em bigram (2-gramas)
# MAGIC * "rougeL": Pontuação baseada em subseqüência comum mais longa.
# MAGIC * "rougeLSum": separa o texto usando "\n"

# COMMAND ----------

display(results.tables["eval_results_table"].head(10))

# COMMAND ----------

# MAGIC %md
# MAGIC E podemos ver resultados resumidos (média, variância etc.) em nível de modelo (em vez de nível de registro) com o seguinte:

# COMMAND ----------

results.metrics

# COMMAND ----------

# MAGIC %md
# MAGIC Também podemos revisar os resultados na interface do usuário de acompanhamento de experimentos do MLflow.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Como é um bom resultado?
# MAGIC
# MAGIC As métricas ROUGE variam entre 0 e 1 – onde 0 indica texto extremamente diferente e 1 indica texto extremamente semelhante. No entanto, nossa interpretação do que é "bom" geralmente será específica para casos de uso. Nem sempre queremos uma pontuação ROUGE próxima de 1 porque provavelmente não reduz muito o tamanho do texto.
# MAGIC
# MAGIC Para explorar o que é "bom", vamos rever alguns de nossos exemplos.

# COMMAND ----------

import pandas as pd
display(
    pd.DataFrame(
        results.tables["eval_results_table"]
    ).loc[0:1, ["inputs", "outputs", "rouge1/v1/score"]]
)

# COMMAND ----------

# MAGIC %md
# MAGIC **Perguntas para discussão:**
# MAGIC 1. Como você interpreta a pontuação ROUGE-1?
# MAGIC 2. As pontuações refletem a sumarização que você acha melhor?

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo 5: Comparando o desempenho do LLM
# MAGIC
# MAGIC Na prática, frequentemente compararemos LLMs (ou sistemas de IA maiores) uns com os outros ao determinar qual é o melhor para nosso caso de uso. Como resultado disso, é importante se familiarizar com a comparação dessas soluções.
# MAGIC
# MAGIC Na célula abaixo, demonstramos como calcular as mesmas métricas usando o mesmo dataset de referência, mas, desta vez, estamos resumindo usando um sistema que utiliza um LLM diferente.
# MAGIC
# MAGIC **Nota:** Desta vez, vamos ler nosso dataset de referência da Delta.

# COMMAND ----------

# A comparar a função personalizada que é usada para iterar através do nosso DataFrame de avaliação
def challenger_query_iteration(inputs):
    answers = []

    for index, row in inputs.iterrows():
        completion = challenger_query_summary_system(row["inputs"])
        answers.append(completion)

    return answers

# Calcular resultados do desafiante
challenger_results = mlflow.evaluate(
    challenger_query_iteration,           # função iterativa acima
    eval_data.head(50),
    targets="writer_summary",             # coluna com saída esperada ou "boa"
    model_type="text-summarization"       # tipo de modelo ou tarefa
)

# COMMAND ----------

# MAGIC %md
# MAGIC Vamos dar uma olhada em nossos resultados em nível de modelo.

# COMMAND ----------

challenger_results.metrics

# COMMAND ----------

# MAGIC %md
# MAGIC E vamos comparar na interface do usuário do MLflow, observando a guia **Gráfico** do experimento.
# MAGIC
# MAGIC **Nota:** Podemos filtrar especificamente para métricas ROUGE.

# COMMAND ----------

# MAGIC %md
# MAGIC E quanto a outras tarefas/métricas?
# MAGIC
# MAGIC A `mlflow` biblioteca contém [várias ferramentas de avaliação de tarefas LLM](https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate) que podemos usar em nossos fluxos de trabalho.

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ## Conclusão
# MAGIC
# MAGIC Agora você deve ser capaz de:
# MAGIC
# MAGIC * Obter dataset de referência/benchmark para avaliação de LLM específico da tarefa
# MAGIC * Avaliar o desempenho de um LLM em uma tarefa específica usando métricas específicas da tarefa
# MAGIC * Comparar o desempenho relativo de dois LLMs usando um conjunto de referência

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
# MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
# MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>
