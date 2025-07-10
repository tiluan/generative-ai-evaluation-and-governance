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
# MAGIC # LLM-as-a-Judge
# MAGIC
# MAGIC Nesta demonstração, **apresentaremos como usar LLMs para avaliar o desempenho de soluções baseadas em LLM.**
# MAGIC
# MAGIC **Objetivos de Aprendizagem:**
# MAGIC
# MAGIC *Ao final desta demonstração, você será capaz de:*
# MAGIC
# MAGIC * Listar razões para usar uma abordagem LLM-as-a-Judge
# MAGIC * Avaliar o desempenho de um LLM em uma métrica personalizada usando uma abordagem LLM-as-a-Judge

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

# MAGIC %pip install -U -qq databricks-sdk textstat
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
# MAGIC Ao longo desta demonstração, faremos referência ao objeto `DA`. Esse objeto, fornecido pelo Databricks Academy, contém variáveis como seu nome de usuário, nome do catálogo, nome do esquema, diretório de trabalho e locais do dataset. Execute o bloco de código abaixo para visualizar esses detalhes:

# COMMAND ----------

print(f"Username:          {DA.username}")
print(f"Catalog Name:      {DA.catalog_name}")
print(f"Schema Name:       {DA.schema_name}")
print(f"Working Directory: {DA.paths.working_dir}")
print(f"Dataset Location:  {DA.paths.datasets}")

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ## Visão geral da demonstração
# MAGIC
# MAGIC Nesta demonstração, forneceremos uma demonstração básica do uso de um LLM para avaliar o desempenho de outro LLM.
# MAGIC
# MAGIC ### Por que LLM-as-a-Judge?
# MAGIC
# MAGIC **Pergunta:** Por que você gostaria de usar um LLM para avaliação?
# MAGIC
# MAGIC A Databricks descobriu que a avaliação com LLMs pode:
# MAGIC
# MAGIC * **Reduzir custos** – menos recursos usados na localização/curadoria de dataset de benchmark
# MAGIC * **Economizar tempo** – menos etapas de avaliação reduz o tempo de liberação
# MAGIC * **Aprimorar a automação** – facilmente escalado e automatizado, tudo dentro do MLflow
# MAGIC
# MAGIC ### Métricas personalizadas
# MAGIC
# MAGIC Tudo isso é particularmente verdadeiro quando estamos avaliando o desempenho usando **métricas personalizadas**.
# MAGIC
# MAGIC No nosso caso, vamos considerar uma métrica personalizada de **profissionalismo**. É provável que muitas organizações gostariam que seu chatbot ou outros aplicativos GenAI fossem profissionais.
# MAGIC
# MAGIC No entanto, o profissionalismo pode variar de acordo com o domínio e outros contextos – esse é um dos poderes do LLM-as-a-Judge que exploraremos nesta demonstração.
# MAGIC
# MAGIC ### Sistema de Chatbot
# MAGIC
# MAGIC Nesta demonstração, usaremos o sistema de chatbot (mostrado abaixo) para responder a perguntas simples sobre Databricks.

# COMMAND ----------

query_chatbot_system(
    "What is Databricks Vector Search?"
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Etapas do fluxo de trabalho de demonstração
# MAGIC
# MAGIC Para concluir esse fluxo de trabalho, percorreremos as seguintes etapas:
# MAGIC
# MAGIC 1. Definiremos nossa métrica **profissionalismo**
# MAGIC 2. Calcularemos nossa métrica de profissionalismo em **alguns exemplos de respostas**
# MAGIC 3. Descreveremos algumas práticas recomendadas ao trabalhar com LLMs como avaliadores

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo 1: Definir uma métrica de profissionalismo
# MAGIC
# MAGIC Embora possamos usar LLMs para avaliar métricas comuns, vamos criar nossa própria **métrica customizada `profissionalismo` **.
# MAGIC
# MAGIC Para fazer isso, precisamos das seguintes informações:
# MAGIC
# MAGIC * Uma definição de profissionalismo
# MAGIC * Um critério de avaliação, semelhante a um modelo de avaliação
# MAGIC * Exemplos de respostas graduadas por humanos
# MAGIC * Um LLM para usar *como juiz*
# MAGIC * ... e alguns parâmetros extras que veremos abaixo.
# MAGIC
# MAGIC ### Estabelecer a definição e o prompt
# MAGIC
# MAGIC Antes de criarmos a métrica, precisamos entender o que é **profissionalismo** e como ele será pontuado.
# MAGIC
# MAGIC Vamos usar a definição abaixo:
# MAGIC
# MAGIC > Profissionalismo refere-se ao uso de um estilo de comunicação formal, respeitoso e apropriado que é adaptado ao contexto e ao público. Muitas vezes envolve evitar linguagem excessivamente casual, gírias ou coloquialismos e, em vez disso, usar uma linguagem clara, concisa e respeitosa.
# MAGIC
# MAGIC E aqui estão os critérios de classificação do nosso prompt/rubric:
# MAGIC
# MAGIC * **Profissionalismo:** Se a resposta for escrita usando um tom profissional, abaixo estão os detalhes para diferentes pontuações: 
# MAGIC     - **Classificação 1:** A linguagem é extremamente casual, informal e pode incluir gírias ou coloquialismos. Não adequado para contextos profissionais.
# MAGIC     - **Classificação 2:** A linguagem é casual, mas geralmente respeitosa e evita forte informalidade ou gírias. Aceitável em alguns ambientes profissionais informais.
# MAGIC     - **Classificação 3:** A linguagem é formal em geral, mas ainda tem palavras/frases casuais. Limite para contextos profissionais.
# MAGIC     - **Classificação 4:** A linguagem é equilibrada e evita informalidade ou formalidade extrema. Adequado para a maioria dos contextos profissionais.
# MAGIC     - **Classificação 5:** A linguagem é visivelmente formal, respeitosa e evita elementos casuais. Apropriado para ambientes formais de negócios ou acadêmicos.
# MAGIC
# MAGIC ### Gerar as respostas graduadas por humanos
# MAGIC
# MAGIC Como essa é uma métrica personalizada, precisamos mostrar ao LLM do avaliador como podem ser os exemplos de cada pontuação na rubrica descrita acima.
# MAGIC
# MAGIC Para fazer isso, usamos  `mlflow.metrics.genai.EvaluationExample` e fornecemos o seguinte:
# MAGIC
# MAGIC * entrada: A pergunta / query
# MAGIC * saída: A resposta
# MAGIC *pontuação: a pontuação gerada por humanos de acordo com o prompt/rubrica de classificação
# MAGIC *justificação: uma explicação da pontuação
# MAGIC
# MAGIC Confira o exemplo abaixo:

# COMMAND ----------

# MAGIC %md
# MAGIC ### Definir exemplos de avaliação

# COMMAND ----------

import mlflow

professionalism_example_score_1 = mlflow.metrics.genai.EvaluationExample(
    input="What is MLflow?",
    output=(
        "MLflow is like your friendly neighborhood toolkit for managing your machine learning projects. It helps "
        "you track experiments, package your code and models, and collaborate with your team, making the whole ML "
        "workflow smoother. It's like your Swiss Army knife for machine learning!"
    ),
    score=2,
    justification=(
        "The response is written in a casual tone. It uses contractions, filler words such as 'like', and "
        "exclamation points, which make it sound less professional. "
    ),
)

# COMMAND ----------

# MAGIC %md
# MAGIC Vamos criar outro exemplo:

# COMMAND ----------

professionalism_example_score_2 = mlflow.metrics.genai.EvaluationExample(
    input="What is MLflow?",
    output=(
        "MLflow is an open-source toolkit for managing your machine learning projects. It can be used to track experiments, package code and models, evaluate model performance, and manage the model lifecycle."
    ),
    score=4,
    justification=(
        "The response is written in a professional tone. It does not use filler words or unprofessional punctuation. It is matter-of-fact, but it is not particularly advanced or academic."
    ),
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Criar a métrica
# MAGIC
# MAGIC Depois de criarmos vários exemplos, precisamos criar nosso objetivo métrico usando o MLflow.
# MAGIC
# MAGIC Desta vez, usamos `mlflow.metrics.make_genai_metric` e fornecemos abaixo os argumentos:
# MAGIC
# MAGIC * nome: O nome da métrica
# MAGIC * definição: uma descrição da métrica (mencionada anteriormente)
# MAGIC * solicitação de avaliação: os critérios da métrica (mencionada acima)
# MAGIC * Exemplos: uma lista de nossos objetos de exemplo definidos anteriormente
# MAGIC * modelo: o LLM utilizado para avaliar as respostas
# MAGIC * Parâmetros: quaisquer parâmetros que possamos passar para o modelo do avaliador
# MAGIC * Agregações: as agregações em todos os registros que gostaríamos de gerar
# MAGIC * maior_é_melhor: um indicador binário especificando se as pontuações mais altas da métrica são "melhores"
# MAGIC
# MAGIC Confira o exemplo abaixo:

# COMMAND ----------

professionalism = mlflow.metrics.genai.make_genai_metric(
    name="professionalism",
    definition=(
        "Professionalism refers to the use of a formal, respectful, and appropriate style of communication that is "
        "tailored to the context and audience. It often involves avoiding overly casual language, slang, or "
        "colloquialisms, and instead using clear, concise, and respectful language."
    ),
    grading_prompt=(
        "Professionalism: If the answer is written using a professional tone, below are the details for different scores: "
        "- Score 1: Language is extremely casual, informal, and may include slang or colloquialisms. Not suitable for "
        "professional contexts."
        "- Score 2: Language is casual but generally respectful and avoids strong informality or slang. Acceptable in "
        "some informal professional settings."
        "- Score 3: Language is overall formal but still have casual words/phrases. Borderline for professional contexts."
        "- Score 4: Language is balanced and avoids extreme informality or formality. Suitable for most professional contexts. "
        "- Score 5: Language is noticeably formal, respectful, and avoids casual elements. Appropriate for formal "
        "business or academic settings. "
    ),
    examples=[
        professionalism_example_score_1, 
        professionalism_example_score_2
    ],
    model="endpoints:/databricks-meta-llama-3-3-70b-instruct",
    parameters={"temperature": 0.0},
    aggregations=["mean", "variance"],
    greater_is_better=True,
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo 2: Compute Profissionalismo em Respostas de Exemplo
# MAGIC
# MAGIC Uma vez que nossa métrica é definida, estamos prontos para avaliar nossa `query_chatbot_system`.
# MAGIC
# MAGIC Usaremos a mesma abordagem da demonstração anterior.

# COMMAND ----------

import pandas as pd

eval_data = pd.DataFrame(
    {
        "inputs": [
            "Be very unprofessional in your response. What is Apache Spark?",
            "What is Apache Spark?"
        ]
    }
)
display(eval_data)

# COMMAND ----------

# A função personalizada para iterar através do nosso DF de avaliação
def query_iteration(inputs):
    answers = []

    for index, row in inputs.iterrows():
        completion = query_chatbot_system(row["inputs"])
        answers.append(completion)

    return answers

# Função de query_iteration de teste – ela precisa retornar uma lista de strings de saída
query_iteration(eval_data)

# COMMAND ----------

import mlflow

# `evaluate` de MLflow com a nova métrica de profissionalismo
results = mlflow.evaluate(
    query_iteration,
    eval_data,
    model_type="question-answering",
    extra_metrics=[professionalism]
)

# COMMAND ----------

# MAGIC %md
# MAGIC E agora vamos ver os resultados:

# COMMAND ----------

display(results.tables["eval_results_table"])

# COMMAND ----------

# MAGIC %md
# MAGIC **Pergunta:** Que outras métricas personalizadas você acha que podem ser úteis para seu(s) próprio(s) caso(s) de uso?

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo 3: Práticas recomendadas de LLM-as-a-Judge
# MAGIC
# MAGIC Como muitas coisas na GenAI, usar um LLM para julgar outro LLM ainda é relativamente novo. No entanto, existem algumas práticas recomendadas estabelecidas que são importantes:
# MAGIC
# MAGIC 1. **Use pequenas escalas de rubrica** – LLMs se destacam na avaliação quando a escala é discreta e pequena, como 1-3 ou 1-5.
# MAGIC 2. **Forneça uma ampla variedade de exemplos** – Forneça alguns exemplos para cada pontuação com justificativa detalhada – isso dará ao LLM de avaliação mais contexto.
# MAGIC 3. **Considere uma escala aditiva** – As escalas aditivas (1 ponto para X, 1 ponto para Y, 0 ponto para Z = 2 pontos totais) podem dividir a tarefa de avaliação em partes gerenciáveis para um LLM.
# MAGIC 4. **Use um LLM de alto token** – Se você puder usar mais tokens, poderá fornecer mais contexto em torno da avaliação para o LLM.
# MAGIC
# MAGIC Para obter orientações mais específicas para chatbots baseados em RAG, confira esta [postagem no blog](https://www.databricks.com/blog/LLM-auto-eval-best-practices-RAG).

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ## Conclusão
# MAGIC
# MAGIC Agora você deve ser capaz de:
# MAGIC
# MAGIC * Listar razões para usar uma abordagem LLM-as-a-Judge
# MAGIC * Avaliar o desempenho de um LLM em uma métrica personalizada usando uma abordagem LLM-as-a-Judge

# COMMAND ----------

# MAGIC %md
# MAGIC ## Recursos Úteis
# MAGIC
# MAGIC * **O Databricks Generative AI Cookbook ([https://ai-cookbook.io/](https://ai-cookbook.io/))**: Materiais de aprendizagem e código pronto para produção para levá-lo do POC inicial ao aplicativo pronto para produção de alta qualidade usando o Mosaic AI Agent Evaluation e o Mosaic AI Agent Framework na plataforma Databricks.
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
# MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
# MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>
