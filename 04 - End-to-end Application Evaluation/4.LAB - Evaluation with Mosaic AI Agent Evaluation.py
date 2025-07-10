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
# MAGIC # LAB- Avaliação com Mosaic AI Agent Evaluation
# MAGIC
# MAGIC Neste laboratório, você terá a oportunidade de avaliar um modelo de RAG chain **usando o Mosaic AI Agent Evaluation Framework.**
# MAGIC
# MAGIC **Esboço do laboratório:**
# MAGIC
# MAGIC *Neste laboratório, você concluirá as seguintes tarefas:*
# MAGIC
# MAGIC - **Tarefa 1**: Defina uma métrica personalizada de avaliação Gen AI.
# MAGIC
# MAGIC - **Tarefa 2**: Realize um teste de avaliação usando o Agent Evaluation Framework.
# MAGIC
# MAGIC - **Tarefa 3**: Analise os resultados da avaliação através da interface do usuário.

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

# MAGIC %pip install -U -qq databricks-agents databricks-vectorsearch langchain-databricks langchain==0.3.7
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC Antes de começar a demonstração, execute o script de configuração de sala de aula fornecido. Esse script definirá as variáveis de configuração necessárias para a demonstração. Execute a seguinte célula:

# COMMAND ----------

# MAGIC %run ../Includes/Classroom-Setup-04

# COMMAND ----------

# MAGIC %md
# MAGIC **Outras Convenções:**
# MAGIC
# MAGIC Ao longo desta demonstração, faremos referência ao objeto `DA`. Esse objeto, fornecido pelo Databricks Academy, contém variáveis como seu nome de usuário, nome do catálogo, nome do esquema, diretório de trabalho e locais de dataset. Execute o bloco de código abaixo para visualizar esses detalhes:

# COMMAND ----------

print(f"Username:          {DA.username}")
print(f"Catalog Name:      {DA.catalog_name}")
print(f"Schema Name:       {DA.schema_name}")
print(f"Working Directory: {DA.paths.working_dir}")
print(f"Dataset Location:  {DA.paths.datasets}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Visão Geral do Laboratório
# MAGIC
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Dataset de Avaliação
# MAGIC
# MAGIC Neste laboratório, você trabalhará com o mesmo dataset utilizado nas demonstrações. Esse dataset contém queries de exemplo junto com suas respostas esperadas correspondentes, que são geradas usando dados sintéticos.

# COMMAND ----------

display(DA.eval_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Carregue o modelo
# MAGIC
# MAGIC Uma RAG chain foi criada e registrada para uso neste laboratório. Os detalhes do modelo são fornecidos abaixo.
# MAGIC
# MAGIC ** Nota:** Se você estiver usando seu próprio espaço de trabalho para executar este laboratório, você deve executar manualmente **`00 - Build Model / 00-Build Model`**.

# COMMAND ----------

import mlflow

catalog_name = "genai_shared_catalog_03"
schema_name = f"ws_{spark.conf.get('spark.databricks.clusterUsageTags.clusterOwnerOrgId')}"

mlflow.set_registry_uri("databricks-uc")

model_uri = f"models:/{catalog_name}.{schema_name}.rag_app/1"
model_name = f"{catalog_name}.{schema_name}.rag_app"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Tarefa 1 - Definir uma métrica personalizada
# MAGIC
# MAGIC Para esta tarefa, defina uma métrica personalizada para avaliar se a **"RESPOSTA"** gerada da RAG chain é facilmente legível por um usuário não especialista.

# COMMAND ----------

from mlflow.metrics.genai import make_genai_metric_from_prompt

# Solicite ao LLM para atuar como juiz para determinar se a resposta gerada é facilmente legível por leitores não-acadêmicos ou não-especialistas
eval_prompt = "Your task is to determine whether the generated response easily readable by non-academic or expert readers. This was the content: '{retrieved_context}'"

# Use Llama-3 como LLM
llm="endpoints:/databricks-meta-llama-3-3-70b-instruct"

# Defina a métrica
is_readable = <FILL_IN>

# COMMAND ----------

# MAGIC %md
# MAGIC ##Tarefa 2 - Executar Teste de Avaliação
# MAGIC
# MAGIC Em seguida, faça a execução de uma avaliação usando a métrica personalizada definida. Certifique-se de selecionar **Mosaic AI Agent Evaluation** como o tipo de avaliação.
# MAGIC

# COMMAND ----------

with <FILL_IN>(run_name="lab_04_agent_evaluation"):
    eval_results = <FILL_IN>

# COMMAND ----------

# MAGIC %md
# MAGIC ## Tarefa 3 - Revisar os resultados da avaliação
# MAGIC
# MAGIC Analise os resultados da avaliação na seção **Experimentos**. Examine as seguintes informações sobre essa avaliação:
# MAGIC
# MAGIC - Uso de tokens
# MAGIC
# MAGIC - Métricas do modelo
# MAGIC
# MAGIC - Resultados da métrica personalizada definida anteriormente ("legibilidade")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conclusão
# MAGIC
# MAGIC Neste laboratório, você avaliou uma RAG chain usando a biblioteca Mosaic AI Evaluation Framework. Você começou carregando o dataset e o modelo RAG. Em seguida, você definiu uma métrica personalizada e iniciou o processo de avaliação. Finalmente, você analisou os resultados por meio da interface do usuário.

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
# MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
# MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>
