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
# MAGIC # Avaliação com Mosaic AI Agent Evaluation
# MAGIC
# MAGIC Em demonstrações anteriores, utilizamos `mlflow` para fins de avaliação. O Mosaic AI Agent Evaluation baseia-se no MLflow, oferecendo recursos e aprimoramentos adicionais. Ele permite a definição de métricas de avaliação personalizadas, facilita a implantação direta do modelo e fornece um **Aplicativo de revisão** fácil de usar.
# MAGIC
# MAGIC **Objetivos de Aprendizagem:**
# MAGIC
# MAGIC *Ao final desta demonstração, você será capaz de:*
# MAGIC
# MAGIC - Carreguar um modelo do registro de modelo e use-o para avaliar um dataset de avaliação.
# MAGIC - Definir métricas de avaliação personalizadas.
# MAGIC - Implante o modelo junto com o App de Revisão para coletar feedback humano.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Requisitos
# MAGIC
# MAGIC Por favor, revise os seguintes requisitos antes de iniciar a lição:
# MAGIC
# MAGIC * Para executar este Notebook, você precisa usar um dos seguintes tempos de execução do Databricks: **15.4.x-cpu-ml-scala2.12**
# MAGIC
# MAGIC ** Aviso de pré-requisito:** Este notebook requer **[00 - Build-Model]($../00-Build-Model/00-Build-Model)** para criar um modelo que será usado para esta demonstração. **No ambiente de laboratório fornecido pelo Databricks, isso será executado antes da aula, o que significa que você não precisa executá-lo manualmente**.

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ## Configuração da Sala de aula
# MAGIC
# MAGIC Instale as bibliotecas necessárias.

# COMMAND ----------

# MAGIC %pip install -U -qq databricks-agents databricks-sdk databricks-vectorsearch langchain-databricks langchain==0.3.7 langchain-community==0.3.7
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
# MAGIC Ao longo desta demonstração, faremos referência ao objeto `DA`. Esse objeto, fornecido pelo Databricks Academy, contém variáveis como seu nome de usuário, nome do catálogo, nome do esquema, diretório de trabalho e locais do dataset. Execute o bloco de código abaixo para visualizar esses detalhes:

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
# MAGIC Nesta demonstração, começaremos revisando **o dataset** que será usado para avaliação. Em seguida, vamos **carregar um modelo de RAG chain** do registro de modelo e utilizá-lo para fins de avaliação. Para ilustrar a avaliação personalizada, definiremos uma métrica personalizada e a incorporaremos ao fluxo de trabalho de avaliação. Após a conclusão da avaliação, vamos **implantar o modelo** e demonstrar como usar o "Review App" integrado para coletar **feedback humano**.
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Prepare o dataset de avaliação
# MAGIC
# MAGIC Esse dataset inclui queries de exemplo e suas respostas esperadas correspondentes. As respostas esperadas são geradas usando dados sintéticos. Em um projeto do mundo real, essas respostas seriam elaboradas por especialistas.

# COMMAND ----------

display(DA.eval_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Carregue o modelo
# MAGIC
# MAGIC Uma RAG chain foi criada e registrada para nós. Se você estiver interessado no código, você pode explorar a pasta `00 - Build Model`. Observe que a construção de  RAG chain está além do escopo deste curso. Para obter mais informações sobre esses tópicos, consulte o curso relacionado, **"Desenvolvimento de Soluções em GenAI"** disponível na Databricks Academy.

# COMMAND ----------

import mlflow

catalog_name = "genai_shared_catalog_03"
schema_name = f"ws_{spark.conf.get('spark.databricks.clusterUsageTags.clusterOwnerOrgId')}"

mlflow.set_registry_uri("databricks-uc")

model_uri = f"models:/{catalog_name}.{schema_name}.rag_app/1"
model_name = DA.register_model(
    model_uri=model_uri,
    catalog_name=catalog_name,
    schema_name=schema_name
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Avaliação do Modelo

# COMMAND ----------

# MAGIC %md
# MAGIC ### Definir Métricas personalizadas
# MAGIC Embora a estrutura de Avaliação de Agentes calcule automaticamente as métricas de avaliação comuns, há instâncias em que talvez seja necessário avaliar o modelo usando métricas personalizadas. Nesta seção, definiremos uma métrica personalizada para avaliar se o **modelo de recuperação** gera respostas contendo personally identifiable information (PII).

# COMMAND ----------

from mlflow.metrics.genai import make_genai_metric_from_prompt

# Defina uma avaliação personalizada para detectar PII nos blocos recuperados. 
has_pii_prompt = "Your task is to determine whether the retrieved content has any PII information. This was the content: '{retrieved_context}'"

has_pii = make_genai_metric_from_prompt(
    name="has_pii",
    judge_prompt=has_pii_prompt,
    model="endpoints:/databricks-meta-llama-3-3-70b-instruct",
    metric_metadata={"assessment_type": "RETRIEVAL"},
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Executar Teste de Avaliação
# MAGIC
# MAGIC Observe que, no código abaixo, estamos registrando o processo de avaliação usando o MLflow para permitir a visualização dos resultados por meio da IU do MLflow.

# COMMAND ----------

with mlflow.start_run(run_name="rag_eval_with_agent_evaluation"):
    eval_results = mlflow.evaluate(
        data = DA.eval_df,
        model = model_uri,
        model_type = "databricks-agent",
        extra_metrics=[has_pii]
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ### Analise os resultados da avaliação
# MAGIC
# MAGIC Temos duas opções para analisar os resultados da avaliação. A primeira opção é examinar as métricas e tabelas diretamente usando o objeto de resultados. A segunda opção é revisar os resultados por meio da interface do usuário (IU).

# COMMAND ----------

# MAGIC %md
# MAGIC #### Revisar Tabela de Resultados

# COMMAND ----------

display(eval_results.metrics)

# COMMAND ----------

display(eval_results.tables['eval_results'])

# COMMAND ----------

# MAGIC %md
# MAGIC ### Revisar os resultados por meio da interface do usuário
# MAGIC
# MAGIC Para exibir os resultados na interface do usuário, execute estas etapas:
# MAGIC
# MAGIC - Clique na tab **"Visualizar resultados da avaliação"** exibido na saída do bloco de código da seção **Executar teste de avaliação** para um método mais simples.
# MAGIC
# MAGIC - Alternativamente, você pode navegar até "Experimentos" no painel esquerdo e localizar o experimento registrado com o título deste notebook.
# MAGIC
# MAGIC - Clique no Nome da execução e Visualize as métricas gerais na guia **Métricas do modelo**.
# MAGIC
# MAGIC - Examine os resultados detalhados de cada avaliação na guia **Pré-visualização dos resultados da avaliação**.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Colete feedback humano via aplicativo de revisão Databricks
# MAGIC
# MAGIC O aplicativo de revisão Databricks prepara o LLM em um ambiente onde as partes interessadas especializadas podem se envolver com ele, permitindo conversas, perguntas e muito mais. Essa configuração possibilita a coleta de feedback valioso sobre sua aplicação, garantindo a qualidade e segurança de suas respostas.
# MAGIC
# MAGIC **As partes interessadas podem interagir com o bot do aplicativo e fornecer feedback sobre essas interações. Eles também podem oferecer feedback sobre logs históricos, rastreamentos selecionados ou saídas de agentes.**
# MAGIC
# MAGIC ** Nota:** Esta etapa destina-se apenas ao instrutor do curso. Se você estiver usando seu próprio ambiente, sinta-se à vontade para comentar as células e executá-las para implantar o modelo e acessar o aplicativo de revisão.

# COMMAND ----------

import time
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import EndpointStateReady, EndpointStateConfigUpdate
import mlflow
from databricks import agents

# Deploy the model with the agent framework
deployment_info = agents.deploy(
    model_name, 
    model_version=1,
    scale_to_zero=True,
    budget_policy_id=None)

# Wait for the Review App and deployed model to be ready
w = WorkspaceClient()
print("\nWaiting for endpoint to deploy.  This can take 15 - 20 minutes.", end="")

while ((w.serving_endpoints.get(deployment_info.endpoint_name).state.ready == EndpointStateReady.NOT_READY) or (w.serving_endpoints.get(deployment_info.endpoint_name).state.config_update == EndpointStateConfigUpdate.IN_PROGRESS)):
    print(".", end="")
    time.sleep(30)

print("\nThe endpoint is ready!", end="")

# COMMAND ----------

print(f"Endpoint URL    : {deployment_info.endpoint_url}")
print(f"Review App URL  : {deployment_info.review_app_url}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Definir permissões para outros usuários
# MAGIC
# MAGIC ** Nota:** Para permitir que outros usuários fazem query e revisem o aplicativo, você precisa definir permissões manualmente. Para fazer isso:
# MAGIC * Vá para a página **Servir** e selecione o endpoint implantado.
# MAGIC
# MAGIC * Selecione **Permissões**.
# MAGIC
# MAGIC * Defina **Pode Query** como "Todos os usuários do espaço de trabalho".

# COMMAND ----------

# MAGIC %md
# MAGIC ## Limpeza
# MAGIC
# MAGIC Você precisa excluir o endpoint implantado para permitir que outras sessões implantem um novo endpoint. Execute a célula abaixo para excluir o endpoint implantado.
# MAGIC
# MAGIC **Nota:** A célula seguinte deve ser executada apenas pelo instrutor. Isso limpará os recursos gerados na seção anterior.

# COMMAND ----------

from mlflow.tracking import MlflowClient
client = MlflowClient()
try:
    print("\nCleaning up resources...")
    # Delete endpoint
    agents.delete_deployment(model_name=model_name)
    print(f"Deleted agent endpoint: {model_name}")
    # Delete payload table
    base_table_name = model_name.split(".")[-1]  # rag_app_<suffix>
    payload_table_name = f"{catalog_name}.{schema_name}.{base_table_name}_payload"
    # Drop the table
    spark.sql(f"DROP TABLE IF EXISTS {payload_table_name}")
    print(f"Deleted table: {payload_table_name}")
    # Delete feedback model
    feedback_model_name = f"{catalog_name}.{schema_name}.feedback"
    client.delete_registered_model(name=feedback_model_name)
    print(f"Deleted feedback model: {feedback_model_name}")
except:
    print("An error occured while trying to delete resources. Please try to delete resources manually! Delete these resources: Model Serving Endpoint, Payload Table, and Feedback Model")

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ## Conclusão
# MAGIC
# MAGIC Nesta demonstração, começamos definindo uma métrica personalizada a ser usada como uma métrica adicional dentro da Estrutura de Avaliação do Agente. Em seguida, realizamos uma execução de avaliação e revisamos os resultados usando a API e a interface do usuário. No passo final, implantamos o modelo por meio do Model Serving e demonstramos como o Review App pode ser utilizado para coletar feedback humano.

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
# MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
# MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>
