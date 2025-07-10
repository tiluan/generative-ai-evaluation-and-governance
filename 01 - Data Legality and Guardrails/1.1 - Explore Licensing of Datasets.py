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
# MAGIC # Explore o licenciamento de dataset
# MAGIC
# MAGIC
# MAGIC **Nesta demonstração, nos concentraremos na revisão das licenças associadas aos dados que podemos querer usar para nosso modelo.** Para fazer isso, exploraremos o Databricks Marketplace. Lá, analisaremos um dataset específico que talvez queiramos usar para um de nossos modelos e encontraremos suas informações de licenciamento.
# MAGIC
# MAGIC
# MAGIC **Objetivos de Aprendizagem:**
# MAGIC
# MAGIC *Ao final desta demonstração, você será capaz de:*
# MAGIC
# MAGIC * Reconhecer possíveis preocupações legais sobre o uso de datasets para seus aplicativos de IA.
# MAGIC
# MAGIC * Encontrará datasets para sua aplicação no Databricks Marketplace.
# MAGIC
# MAGIC * Avalie com seu advogado se a licença para um determinado dataset permitiria seu uso pretendido.
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Requisitos
# MAGIC
# MAGIC Por favor, revise os seguintes requisitos antes de iniciar a lição:
# MAGIC
# MAGIC * Para percorrer esta demonstração, você simplesmente precisa de um ambiente Databricks com acesso ao **[Databricks Marketplace](/marketplace)**.
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Visão geral da demonstração
# MAGIC
# MAGIC O poder dos aplicativos modernos de GenAI está em sua capacidade de se familiarizar intimamente com os dados da sua empresa. No entanto, também há casos de uso em que podemos querer aumentar nossos dados de treinamento ou dados de conhecimento contextual com dados gerais do setor. Podemos encontrar dados complementares usando o Databricks Marketplace.
# MAGIC
# MAGIC Nesta demonstração, exploraremos alguns datasets no Databricks Marketplace, com um foco particular em questões de licenciamento e determinar se eles seriam um bom candidato para uso em um tipo específico de aplicativo GenAI.
# MAGIC
# MAGIC Aqui estão todas as etapas detalhadas:
# MAGIC
# MAGIC - Familiarize-se com o Databricks Marketplace e como encontrá-lo.
# MAGIC - Olhe para a licença para um dataset de exemplo que seria OK para o nosso aplicativo.
# MAGIC - Explore outro dataset de exemplo que pode não ser OK para usarmos.
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Databricks Marketplace
# MAGIC
# MAGIC O Databricks Marketplace permite que os usuários descubram, explorem e acessem dados e recursos de IA de uma variedade de fornecedores. Ele oferece recursos como datasets que você pode usar para alimentar aplicativos RAG ou adicionar como recursos ou atributos a seus pipelines existentes, modelos de machine learning pré-treinados e aceleradores de solução para ajudá-lo a passar do conceito à produção de forma mais rápida e eficiente.
# MAGIC
# MAGIC ![marketplace_home](files/images/generative-ai-evaluation-and-governance-2.0.2/marketplace_home.png)
# MAGIC
# MAGIC Nesta demonstração, nos concentraremos nos datasets que podemos usar para nosso aplicativo RAG.
# MAGIC
# MAGIC Há **duas razões principais** que podemos querer encontrar dados adicionais para o nosso aplicativo RAG:
# MAGIC
# MAGIC 1. Podemos querer dados de referência adicionais para aumentar nosso prompt como contexto que podemos fazer query em tempo de execução usando a Vector Search em um índice Vector.
# MAGIC 2. Em alguns cenários, talvez precisemos de dados adicionais para usar para fine-tuning ou fazer mais pré-treinamento no LLM alimentando nosso aplicativo RAG geral – observe que isso também pode ser aplicado fora dos aplicativos RAG.
# MAGIC
# MAGIC ### Por que queremos dados de terceiros?
# MAGIC
# MAGIC É verdade que muitos dos dados contextuais do seu aplicativo provavelmente virão de dentro da sua empresa. No entanto, pode haver momentos em que as informações fornecidas por fornecedores terceirizados também podem ser úteis. Precisamos ter certeza de que temos permissão para usar esses dados.
# MAGIC
# MAGIC Como profissionais, é fundamental estar ciente das possíveis restrições de licenciamento que esses datasets podem trazer e que podem impedir que você use aquele dataset específico para a finalidade pretendida. Cada dataset no Databricks Marketplace deve ter uma licença que você pode revisar para determinar (junto com seu consultor jurídico apropriado) se ele é utilizável ou não.
# MAGIC
# MAGIC **Observação:** embora o foco aqui seja o Databricks Marketplace, as mesmas ideias são igualmente aplicáveis aos dados que você encontra em qualquer outro lugar na interface, incluindo outros hubs de dados como o hospedado e operado pela Hugging Face. Independentemente de onde você encontrar dados para seu aplicativo, certifique-se de conhecer as implicações legais e de licenciamento.
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Dataset de avaliações da Amazon da Bright Data
# MAGIC
# MAGIC No primeiro exemplo, veremos um dataset de avaliações da Amazon da Bright Data. 
# MAGIC
# MAGIC Para localizar o dataset, siga as etapas abaixo:
# MAGIC
# MAGIC 1. Navegue até o Databricks Marketplace
# MAGIC 2. filtrar o filtro **Produto** para "Tabelas"
# MAGIC 3. Filtrar o filtro **Fornecedor** para "Bright Data"
# MAGIC 4. Abra o dataset "Amazon - Produtos Mais Vendidos / Avaliações / Dataset de Produtos"
# MAGIC
# MAGIC ![bright_data_amazon_reviews_dataset_overview](files/images/generative-ai-evaluation-and-governance-2.0.2/bright_data_amazon_reviews_dataset_overview.png)
# MAGIC
# MAGIC Vamos explorar os dados para ver se eles podem funcionar no nosso caso de uso:
# MAGIC
# MAGIC * Qual é o nível de registro do dataset?
# MAGIC * Quais campos ele inclui?
# MAGIC * Quantos registros ele tem?
# MAGIC * Com que frequência os dados são atualizados?
# MAGIC
# MAGIC Mesmo que o dataset atenda aos nossos requisitos, precisamos revisar sua **licença** para determinar se temos ou não permissão para usá-lo.
# MAGIC
# MAGIC Para encontrar as informações da licença:
# MAGIC
# MAGIC 1. Dê uma olhada na seção **Links de produtos** nas informações do fornecedor
# MAGIC 2. Clique em **Licença** para abrir as informações da licença
# MAGIC 3. Procure no contrato algo como "Uso aceitável"
# MAGIC
# MAGIC Você precisará revisar cuidadosamente a licença para determinar se ela permite o uso pretendido com a sua aplicação. É altamente recomendável aproveitar a assessoria jurídica ao tomar qualquer decisão sobre licenciamento.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Rearc Informações Pessoais | FRED
# MAGIC
# MAGIC No próximo exemplo, veremos um dataset de renda pessoal da Rearc.
# MAGIC
# MAGIC ![rearc_personal_income_fred_overview](files/images/generative-ai-evaluation-and-governance-2.0.2/rearc_personal_income_fred_overview.png)
# MAGIC
# MAGIC Vamos começar com algumas perguntas:
# MAGIC
# MAGIC * Como esses dados seriam úteis para uma aplicação de GenAI?
# MAGIC * Onde está a informação da licença?
# MAGIC * Podemos usar esses dados para uma hipotética aplicação comercial?
# MAGIC
# MAGIC A mesma orientação se aplica aqui. Analise cuidadosamente a licença, idealmente com a ajuda de um advogado apropriado antes de integrar os dados em seu aplicativo ou usá-los para o treinamento ou ajuste de seus modelos.
# MAGIC
# MAGIC ### Ingestão dos dados
# MAGIC
# MAGIC Vamos supor que tenhamos permissão legal para usar os dados para nosso caso de uso.
# MAGIC
# MAGIC Podemos importá-lo em nosso ambiente diretamente do Databricks Marketplace clicando no botão **Obter acesso instantâneo** na página do dataset no Marketplace.
# MAGIC
# MAGIC Isso nos pedirá para:
# MAGIC
# MAGIC * determinar o nome do catálogo no qual os dados residirão (novos ou existentes).
# MAGIC * aceitar os termos e condições.
# MAGIC
# MAGIC E então poderemos abrir, explorar e usar nossos dados!

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conclusão
# MAGIC
# MAGIC Antes de usar qualquer dataset externo para seu aplicativo, você precisa revisar as informações de licenciamento sob as quais ele é fornecido. Os dados disponibilizados através do Databricks Marketplace devem sempre ter um local para encontrar as informações de licença, que recomendamos que você analise a si mesmo como profissional, bem como com o conselho de um advogado apropriado. Outros hubs populares, como o Hugging Face, também devem ter informações de licença disponíveis para cada dataset.

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
# MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
# MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>
