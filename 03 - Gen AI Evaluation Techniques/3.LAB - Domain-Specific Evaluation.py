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
# MAGIC # LAB - Avaliação específica por domínio 
# MAGIC
# MAGIC
# MAGIC Neste laboratório, você terá a oportunidade de avaliar um large language model em uma tarefa específica **usando um dataset projetado para essa avaliação exata.**
# MAGIC
# MAGIC **Esboço do laboratório:**
# MAGIC
# MAGIC *Neste laboratório, você precisará concluir as seguintes tarefas:*
# MAGIC
# MAGIC - **Tarefa 1:** Criar um benchmark dataset
# MAGIC - **Tarefa 2:** Calcular ROUGE em Benchmark de Dados Personalizados
# MAGIC - **tarefa 3:** Use uma abordagem de 'LLM-as-a-Judge' para avaliar métricas personalizadas

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

# MAGIC %pip install -U -qq databricks-sdk rouge_score textstat
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC Antes de iniciar o laboratório, execute o script de configuração de sala de aula fornecido. Esse script definirá as variáveis de configuração necessárias para o laboratório. Execute a seguinte célula:

# COMMAND ----------

# MAGIC %run ../Includes/Classroom-Setup-03

# COMMAND ----------

# MAGIC %md
# MAGIC **Outras Convenções:**
# MAGIC
# MAGIC Ao longo deste laboratório, faremos referência ao objeto `DA`. Esse objeto, fornecido pelo Databricks Academy, contém variáveis como seu nome de usuário, nome do catálogo, nome do esquema, diretório de trabalho e locais do dataset. Execute o bloco de código abaixo para visualizar esses detalhes:

# COMMAND ----------

print(f"Username:          {DA.username}")
print(f"Catalog Name:      {DA.catalog_name}")
print(f"Schema Name:       {DA.schema_name}")
print(f"Working Directory: {DA.paths.working_dir}")
print(f"Dataset Location:  {DA.paths.datasets}")

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC # Visão Geral do Laboratório
# MAGIC
# MAGIC Neste laboratório, você estará novamente avaliando o desempenho de um sistema de IA projetado para resumir texto.

# COMMAND ----------

query_product_summary_system(
    "This is the best frozen pizza I've ever had! Sure, it's not the healthiest, but it tasted just like it was delivered from our favorite pizzeria down the street. The cheese browned nicely and fresh tomatoes are a nice touch, too! I would buy it again despite it's high price. If I could change one thing, I'd made it a little healthier – could we get a gluten-free crust option? My son would love that."
)

# COMMAND ----------

# MAGIC %md
# MAGIC No entanto, você avaliará o LLM usando um conjunto de benchmark selecionado específico para nossa avaliação.
# MAGIC
# MAGIC Este laboratório seguirá os passos abaixo:
# MAGIC
# MAGIC 1. Criar um benchmark dataset personalizado específico para o caso de uso
# MAGIC 2. Calcular métricas de avaliação específicas de resumo usando o benchmark dataset personalizado
# MAGIC 3. Usar uma abordagem de LLM-as-a-Judge para avaliar métricas personalizadas

# COMMAND ----------

# MAGIC %md
# MAGIC ## Tarefa 1: Criar um benchmark dataset
# MAGIC
# MAGIC Lembre-se de que o ROUGE requer conjuntos de referência para calcular pontuações. Em nossa demonstração, usamos um conjunto de benchmark grande e genérico.
# MAGIC
# MAGIC Neste laboratório, você precisa usar um conjunto de benchmark específico do domínio para o caso de uso.
# MAGIC
# MAGIC ### Conjunto de benchmark específico do caso
# MAGIC
# MAGIC Embora o dataset específico da base provavelmente não seja tão grande, ele tem a vantagem de ser mais representativo da tarefa que estamos realmente pedindo ao LLM para executar.
# MAGIC
# MAGIC Abaixo, começamos a criar um dataset para resumos de revisão de produtos de supermercado. É sua tarefa criar mais dois resumos de produtos para este dataset.
# MAGIC
# MAGIC **Dica:** Tente abrir outra tab e usar o AI Playground para gerar alguns exemplos! Apenas certifique-se de verificá-los manualmente, pois estes são os nossos dados de referência para avaliação.
# MAGIC
# MAGIC **Nota:** Para esta tarefa, estamos criando um conjunto de referência *extremamente pequeno*. Na prática, você vai querer criar um com muito mais exemplos de registros.

# COMMAND ----------


import pandas as pd

eval_data = pd.DataFrame(
    {
        "inputs": [
            "This coffee is exceptional. Its intensely bold flavor profile is both nutty and fruity – especially with notes of plum and citrus. While the price is relatively good, I find myself needing to purchase bags too often. If this came in 16oz bags instead of just 12oz bags, I'd purchase it all the time. I highly recommend they start scaling up their bag size.",
            "The moment I opened the tub of Chocolate-Covered Strawberry Delight ice cream, I was greeted by the enticing aroma of fresh strawberries and rich chocolate. The appearance of the ice cream was equally appealing, with a swirl of pink strawberry ice cream and chunks of chocolate-covered strawberries scattered throughout. The first bite did not disappoint. The strawberry ice cream was creamy and flavorful, with a natural sweetness that was not overpowering. The chocolate-covered strawberries added a satisfying crunch fruity bite.",
            "Arroz Delicioso is a must-try for Mexican cuisine enthusiasts! This authentic Mexican rice, infused with a blend of tomatoes, onions, and garlic, brings a burst of flavor to any meal. Its vibrant color and delightful aroma will transport you straight to the heart of Mexico. The rice cooks evenly, resulting in separate, fluffy grains that hold their shape, making it perfect for dishes like arroz con pollo or as a side for tacos. With a cook time of just 20 minutes, Arroz Delicioso is a convenient and delicious addition to your pantry. Give it a try and elevate your Mexican food game!",
            "FreshCrunch salad mixes are revolutionizing the way we think about packaged salads! Each bag is packed with a vibrant blend of crisp, nutrient-rich greens, including baby spinach, arugula, and kale. The veggies are pre-washed and ready to eat, making meal prep a breeze. FreshCrunch sets itself apart with its innovative packaging that keeps the greens fresh for up to 10 days, reducing food waste and ensuring you always have a healthy option on hand. The salad mixes are versatile and pair well with various dressings and toppings. Try FreshCrunch for a convenient, delicious, and nutritious meal solution that doesn't compromise on quality or taste!",
            <FILL_IN>,
            <FILL_IN>
        ],
        "ground_truth": [
            "This bold, nutty, and fruity coffee is delicious, and they need to start selling it in larger bags.",
            "Chocolate-Covered Strawberry Delight ice cream looks delicious with its aroma of strawberry and chocolate, and its creamy, naturally sweet taste did not disappoint.",
            "Arroz Delicioso offers authentic, flavorful Mexican rice with a blend of tomatoes, onions, and garlic, cooking evenly into separate, fluffy grains in just 20 minutes, making it a convenient and delicious choice for dishes like arroz con pollo or as a side for tacos.",
            "FreshCrunch salad mixes offer convenient, pre-washed, nutrient-rich greens in an innovative packaging that keeps them fresh for up to 10 days, providing a versatile, tasty, and waste-reducing healthy meal solution.",
            <FILL_IN>,
            <FILL_IN>
        ],
    }
)

display(eval_data)

# COMMAND ----------

# MAGIC %md
# MAGIC Pergunta: Quais são algumas estratégias para avaliar seu benchmark dataset gerado personalizadamente? Por exemplo:
# MAGIC * Como você pode escalar a curadoria?
# MAGIC * Como saber se o ground truth está correto?
# MAGIC * Quem deve ter participação?
# MAGIC * Deve permanecer estático ao longo do tempo?
# MAGIC
# MAGIC Em seguida, estamos salvando esse dataset de referência para uso futuro.

# COMMAND ----------

spark_df = spark.createDataFrame(eval_data)
spark_df.write.mode("overwrite").saveAsTable(f"{DA.catalog_name}.{DA.schema_name}.case_spec_summ_eval")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Tarefa 2: Calcule ROUGE em dados de benchmark personalizados
# MAGIC
# MAGIC Em seguida, vamos querer calcular nossa métrica ROUGE-N para entender como nosso sistema resume bem as avaliações de produtos de supermercado com base na referência de avaliações que acabou de ser criada.
# MAGIC
# MAGIC Lembre-se de que a `mlflow.evaluate` função aceita os seguintes parâmetros para esse caso de uso:
# MAGIC
# MAGIC * Um modelo LLM
# MAGIC * Dados de referência para avaliação
# MAGIC * Coluna com dados de referência
# MAGIC * O modelo/tipo de tarefa (por exemplo `"text-summarization"`)
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ### Passo 2.1: Execute a avaliação
# MAGIC
# MAGIC Em vez de usar o benchmark dataset genérico como na demonstração, sua tarefa é **Computar métricas ROUGE usando os dados de benchmark específicos de cada caso que acabamos de criar.**
# MAGIC
# MAGIC **Nota:** Se necessário, consulte a demonstração para completar os blocos de código abaixo.
# MAGIC
# MAGIC Primeiro, a função que você pode usar para iterar pelas linhas para `mlflow.evaluate`.

# COMMAND ----------


# A função personalizada para iterar através do nosso DF de avaliação
def query_iteration(inputs):
    answers = []

    for index, row in inputs.iterrows():
        <FILL_IN>

    return answers

# Função de query_iteration de teste – ela precisa retornar uma lista de strings de saída
query_iteration(eval_data)

# COMMAND ----------

# MAGIC %md
# MAGIC Em seguida, utilize a função anterior e `mlflow.evaluate` para realizar a avaliação `text-summarization` .

# COMMAND ----------


import mlflow

# Avaliar com uma função personalizada
results = <FILL_IN>

# COMMAND ----------

# MAGIC %md
# MAGIC ### Etapa 2.2: Avalie os resultados
# MAGIC
# MAGIC A seguir, dê uma olhada nos resultados.

# COMMAND ----------


display(results<FILL_IN>)

# COMMAND ----------

# MAGIC %md
# MAGIC **Pergunta:** Como interpretamos esses resultados? O que isso nos diz sobre a qualidade do resumo? Sobre nosso LLM?
# MAGIC
# MAGIC Em seguida, calcular as métricas resumidas para exibir o desempenho do LLM em todo o dataset.

# COMMAND ----------

<FILL_IN>

# COMMAND ----------

# MAGIC %md
# MAGIC **Bônus:** Dê uma olhada nos resultados na interface do usuário de acompanhamento de experimentos.
# MAGIC
# MAGIC Você vê algum resumo que você acha que é particularmente bom ou problemático?

# COMMAND ----------

# MAGIC %md
# MAGIC ## Tarefa 3: Use a Abordagem LLM-as-a-Judge para avaliar métricas personalizadas
# MAGIC
# MAGIC Nesta tarefa, você definirá e avaliará uma métrica personalizada chamada "profissionalismo" usando a Abordagem LLM-as-a-Judge. O objetivo é avaliar a qualidade profissional dos resumos gerados pelo modelo de linguagem, com base em um conjunto de critérios predefinidos.
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ### Passo 3.1: Definir uma métrica de humor
# MAGIC
# MAGIC - Defina humor e crie um prompt de avaliação.
# MAGIC
# MAGIC   **A fazer:**
# MAGIC
# MAGIC   Para esta tarefa, você recebe um exemplo inicial de humor (humor_example_score_1). Sua tarefa é gerar outro exemplo de avaliação (humor_example_score_2). 
# MAGIC
# MAGIC   **Dica:** Você pode usar o AI Playground para isso. Certifique-se de que o exemplo gerado seja relevante para o prompt e reflita uma pontuação de humor diferente. Verifique manualmente o exemplo gerado para garantir sua correção.
# MAGIC

# COMMAND ----------


# Defina um exemplo de avaliação para humor com pontuação 2
humor_example_score_1 = mlflow.metrics.genai.EvaluationExample(
    input="Tell me a joke!",  
    output=(
        "Why don't scientists trust atoms? Because they make up everything!"  
    ),
    score=2, # Pontuação de humor atribuído ao resultado
    justification=(
        "The joke uses a common pun and is somewhat humorous, but it may not elicit strong laughter or amusement from everyone."  # Justificativa para a pontuação atribuída
    ),
)

# Defina outro exemplo de avaliação para humor com pontuação 4
humor_example_score_2 = <FILL_IN>
    input=<FILL_IN>,  
    output=(
        <FILL_IN> 
    ),
    score=<FILL_IN>   # Pontuação de humor atribuída à saída
    justification=(
        <FILL_IN>
         # Justificativa para a pontuação atribuída
    ),
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Passo 3.2: LLM-as-a-Judge para comparar métricas
# MAGIC
# MAGIC * **3.2.1:  Crie uma métrica para comparar as respostas de humor**
# MAGIC
# MAGIC   Defina uma métrica personalizada para avaliar o humor nas respostas geradas. Essa métrica avaliará o nível de humor presente nas respostas geradas pelo modelo de linguagem.

# COMMAND ----------


# Defina a métrica para a avaliação
comparison_humor_metric = mlflow.metrics.genai.make_genai_metric(
    name="comparison_humor",
    definition=(
        "Humor refers to the ability to evoke laughter, amusement, or enjoyment through cleverness, wit, or unexpected twists."
    ),
    grading_prompt=(
        "Humor: If the response is funny and induces laughter or amusement, below are the details for different scores: "
        "- Score 1: The response attempts humor but falls flat, eliciting little to no laughter or amusement."
        "- Score 2: The response is somewhat humorous, eliciting mild laughter or amusement from some individuals."
        "- Score 3: The response is moderately funny, eliciting genuine laughter or amusement from most individuals."
        "- Score 4: <FILL_IN>"
        "- Score 5: <FILL_IN>"
    ),
    # Exemplos de humor
    examples=[
        <FILL_IN>
    ],
    model="endpoints:/databricks-meta-llama-3-3-70b-instruct",
    parameters={"temperature": 0.0},
    aggregations=["mean", "variance"],
    greater_is_better=True,
)

# COMMAND ----------

# MAGIC %md
# MAGIC * **3.2.3: Gere dados com diferentes níveis de humor**
# MAGIC
# MAGIC   Adicione prompts de entrada e respostas de saída correspondentes com diferentes níveis de humor. 
# MAGIC   
# MAGIC   **Dica:** Você pode utilizar AI Playgrounds para gerar esses valores.

# COMMAND ----------

# Defina dados de teste com diferentes pontuações de humor para comparação
humor_data = pd.DataFrame(
    {
        "inputs": [
            
            <FILL_IN>
        ],
        "ground_truth": [
            <FILL_IN>
        ],
    }
)

# COMMAND ----------

# MAGIC %md
# MAGIC * **3.2.4: Avalie a comparação**
# MAGIC
# MAGIC   A seguir, avalie a comparação entre as respostas geradas pelo modelo de linguagem. Essa avaliação fornecerá uma métrica para avaliar o profissionalismo dos resumos gerados com base em critérios predefinidos.
# MAGIC

# COMMAND ----------

benchmark_comparison_results = <FILL_IN>

# COMMAND ----------

# MAGIC %md
# MAGIC * **3.2.5: Visualizar Resultados da comparação**
# MAGIC
# MAGIC   Agora, vamos dar uma olhada nos resultados da comparação entre as respostas geradas pelo modelo de linguagem. Essa comparação fornece percepções sobre o profissionalismo dos resumos gerados com base nos critérios predefinidos.
# MAGIC

# COMMAND ----------

display(benchmark_comparison_results.<FILL_IN>)

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ## Conclusão
# MAGIC
# MAGIC Este laboratório forneceu uma experiência prática na criação e avaliação de um benchmark dataset personalizado, computação de métricas de avaliação específicas de tarefas e aproveitamento de uma abordagem LLM-as-a-Judge para avaliar métricas personalizadas. Essas técnicas são essenciais para avaliar o desempenho de sistemas de IA em tarefas específicas de domínio e garantir sua eficácia em aplicações do mundo real.

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
# MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
# MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>
