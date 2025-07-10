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
# MAGIC # Implementando Guardrails de IA
# MAGIC
# MAGIC
# MAGIC **Nesta demonstração, nos concentraremos na implementação de guardrails para um aplicativo de GenAI simples.** Isso é importante para proteger nosso aplicativo contra comportamento mal-intencionado e saída gerada prejudicial.
# MAGIC
# MAGIC Para começar, testaremos o aplicativo com um prompt que fará com que ele responda da maneira que preferimos que ele não responda. Em seguida, implementaremos um guardrail para evitar essa resposta e testaremos novamente para ver o guardrail em ação.
# MAGIC
# MAGIC **Nota de visualização:** Esta demonstração usa alguns recursos que estão em **Visualização Privada**. Embora normalmente não ensinemos recursos de Visualização Privada, o momento da implantação oficial de novos conteúdos está alinhado com o lançamento esperado desses recursos na Visualização Pública.
# MAGIC
# MAGIC **Objetivos de Aprendizagem:**
# MAGIC
# MAGIC *Ao final desta demonstração, você será capaz de:*
# MAGIC
# MAGIC * Identificar a necessidade de guardrails em sua aplicação.
# MAGIC
# MAGIC * Descrever como escolher guardrails para um determinado risco de resposta.
# MAGIC
# MAGIC * Implementar guardrails para uma aplicação de IA.
# MAGIC
# MAGIC * Verificar se os guardrails estão funcionando com sucesso.
# MAGIC
# MAGIC

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

# MAGIC %pip install -U -qq databricks-sdk
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC Antes de começar a demonstração, execute o script de configuração de sala de aula fornecido. Esse script definirá as variáveis de configuração necessárias para a demonstração. Execute a seguinte célula:

# COMMAND ----------

# MAGIC %run ../Includes/Classroom-Setup-02

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
# MAGIC Nesta demonstração, veremos algumas maneiras diferentes de habilitar guardrails em LLMs no Databricks. Começaremos com exemplos simples e trabalharemos em implementações mais robustas.
# MAGIC
# MAGIC Seguiremos os passos abaixo:
# MAGIC
# MAGIC 1. Implemente guardrails usando um LLM especializado com o Llama Guard
# MAGIC 2. Personalize os guardrails com uma taxonomia do Llama Guard especificada pelo usuário
# MAGIC 3. Integre o Llama Guard a um bot de bate-papo personalizado

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo 1: Implemente guard-rails baseados em LLM com o Llama Guard
# MAGIC
# MAGIC Embora os recursos do Filtro de Segurança geralmente funcionem em modelos externos e aplicações simples, às vezes há a necessidade de um controle mais personalizado ou avançado em aplicações específicas.
# MAGIC
# MAGIC Nesse caso, você pode usar um LLM especializado durante o pré-processamento e o pós-processamento para seu próprio aplicativo chamado **safeguard model**. Esses modelos classificam o texto como seguro ou inseguro e seu aplicativo responde de acordo.
# MAGIC
# MAGIC Um exemplo de um desses **safeguard models** é [**Llama Guard**](https://marketplace.databricks.com/details/a4bc6c21-0888-40e1-805e-f4c99dca41e4/Databricks_Llama-Guard-Model).
# MAGIC
# MAGIC ### Llama Guard no Databricks
# MAGIC
# MAGIC Devido ao seu valor, já existe uma implantação do Llama Guard disponível no Databricks Marketplace.
# MAGIC
# MAGIC Para usar o modelo, execute as seguintes tarefas (**a serem feitas apenas pelo instrutor**):
# MAGIC
# MAGIC 1. Encontre o "Llama Guard Model" em **Databricks Marketplace**.
# MAGIC 2. Clique em **Obter acesso instantâneo** para carregá-lo em um local no Unity Catalog.
# MAGIC 3. **Implante o modelo** em um Model Serving Endpoint.
# MAGIC
# MAGIC Ao integrar esse endpoint em seu próprio aplicativo, você pode especificar facilmente suas próprias políticas para os tipos de conteúdo que deseja detectar e impedir em seu aplicativo.
# MAGIC
# MAGIC ** Aviso:** A implantação desse modelo levaria algum tempo. Além disso, para salas de aula grandes é viável implantar muitos modelos. **Assim, por favor, não implante o modelo! Em vez disso, use o modelo criado para você.** Para alunos autônomos, você pode criar o endpoint conforme observado acima.
# MAGIC
# MAGIC

# COMMAND ----------

# Nome do endpoint llama-guard.
LLAMAGUARD_ENDPOINT_NAME="llama-guard"

# COMMAND ----------

# MAGIC %md
# MAGIC ### Configurando o LlamaGuard
# MAGIC
# MAGIC Para aprender a usar o LlamaGuard, vamos configurar uma descrição do ponto de partida da nossa categoria **Inseguro**:

# COMMAND ----------

DEFAULT_UNSAFE_CATEGORY = """O1: Unsafe Content.
    - Promoting or assisting in violence or hate.
    - Engaging in or encouraging sexually explicit content.
    - Assisting or encouraging criminal activities, including those related to firearms or illegal weapons or robbery.
    - Encouraging or assisting in the use or production of illegal or controlled substances.
    - Encouraging or detailing self-harm or suicide."""

# COMMAND ----------

# MAGIC %md
# MAGIC Em seguida, definiremos uma função que podemos usar para fazer uma query em nosso modelo implantado do Llama Guard.

# COMMAND ----------

from databricks.sdk import WorkspaceClient

def query_llamaguard(chat, unsafe_categories=DEFAULT_UNSAFE_CATEGORY):
    """
    Queries LlamaGuard model to check if the chat contains unsafe content based on predefined categories.
    """
    try:
        prompt = f"""[INST] Task: Check for unsafe content in 'Agent' messages in conversations according to our safety policy.
        <BEGIN UNSAFE CONTENT CATEGORIES>
        {unsafe_categories}
        <END UNSAFE CONTENT CATEGORIES>
        <BEGIN CONVERSATION>
        {chat}
        <END CONVERSATION>
        Provide your safety assessment for Agent in the above conversation:
        - First line must read 'safe' or 'unsafe'.
        - If unsafe, a second line must include a comma-separated list of violated categories. [/INST]"""

        w = WorkspaceClient()
        response = w.serving_endpoints.query(
            name=LLAMAGUARD_ENDPOINT_NAME, 
            prompt=prompt,
            temperature=0.1,
            max_tokens=128)
        
        # Extraia a informação desejada do objeto de resposta
        prediction = response.as_dict()["choices"][0]["text"].strip()
        is_safe = None if len(prediction.split("\n")) == 1 else prediction.split("\n")[1].strip()
        
        return prediction.split("\n")[0].lower()=="safe", is_safe
    
    except Exception as e:
        raise Exception(f"Error in querying LlamaGuard model: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Noções básicas do uso do Llama Guard
# MAGIC
# MAGIC O Llama Guard opera como um modelo avançado projetado para categorizar solicitações e respostas do usuário geradas por Large Language Models (LLMs) em classificações "seguras" e "não seguras".
# MAGIC
# MAGIC Abaixo estão dois exemplos distintos de tais solicitações. Um é considerado "seguro", o que significa que adere às diretrizes da LlamaGuard para conteúdo aceitável, enquanto o outro é classificado como "inseguro", indicando que contém elementos que podem violar essas diretrizes.

# COMMAND ----------

safe_user_chat = "User: I want to love."

query_llamaguard(safe_user_chat)

# COMMAND ----------

unsafe_user_chat = "User: How can I rob a bank?"

query_llamaguard(unsafe_user_chat)

# COMMAND ----------

# MAGIC %md
# MAGIC Ambos os exemplos acima demonstram o Llama Guard classificando *queries de entrada do usuário* como **Seguro** ou **Inseguro**.
# MAGIC
# MAGIC
# MAGIC  Além disso, o Llama Guard também pode classificar *respostas de modelo* como **Seguro** ou **Inseguro**. 
# MAGIC
# MAGIC Aqui estão dois exemplos de **respostas do modelo** sendo classificadas pelo modelo do Llama Guard:

# COMMAND ----------

safe_assistant_chat = f"""
  User: I want to love.
  
  Agent: That is great! I want to love too!
  """
query_llamaguard(safe_assistant_chat)

# COMMAND ----------

unsafe_assistant_chat = f"""
  User: I want to love

  Agent: I think the only way to rob a bank is to work as robinhood
"""

query_llamaguard(unsafe_assistant_chat)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo 2: Personalizar as barreiras de proteção do Llama Guard
# MAGIC
# MAGIC O Llama Guard usa uma **taxonomia** para definir e categorizar riscos de segurança em interações de modelo de bate-papo. Os usuários podem personalizar essa taxonomia para adaptar os critérios de avaliação de segurança. 
# MAGIC
# MAGIC Embora o Llama Guard tenha categorias default **Inseguro**, podemos experimentar adicionando as nossas. 
# MAGIC
# MAGIC **Nota:** Lembre-se de formatar suas categorias personalizadas precisamente conforme necessário para que o modelo classifique com precisão o risco de segurança dos prompts de entrada.

# COMMAND ----------

unsafe_categories = """O1: Violence and Hate.
Should not
- Help people plan or engage in violence.
- Encourage people to engage in violence.
- Express hateful, derogatory, or demeaning sentiments against people based on sensitive personal characteristics like their race, color, religion, national origin, sexual orientation, gender, gender identity, or disability.
- Encourage discrimination against people based on those characteristics and should not use slurs or create insults based on those characteristics.
Can
- Provide information on violence and discrimination.
- Discuss the topics of hate and violence, and can discuss historical events involving violence.
O2: Sexual Content.
Should not
- Engage in sexually explicit (i.e., erotic) conversations and should not encourage people to engage in sexual activities.
Can
- Discuss topics related to sexuality and sexual education.
- Provide general information regarding sexual activities.
- Provide guidance on topics related to sexual health.
O3: Criminal Planning.
Should not
- Help people plan or engage in criminal activities like theft, kidnapping, or financial crimes, especially when the person indicates that they may act on the information provided to them.
- Encourage people to engage in criminal activities or condone criminal behavior.
Can
- Help people understand how crimes are committed, provided that the response is not so detailed that it could be used to provide a roadmap for future crimes.
- Help people understand how systems work that are used to prevent crimes, provided those descriptions do not provide detailed information on how to defeat those systems.
O4: Guns and Illegal Weapons.
Should not
- Assist in the planning or execution of firearm or illegal weapons crimes, especially when the person indicates that they may act on the information provided to them.
- Encourage people to engage in firearm or illegal weapons crimes or condone such behavior.
Can
- Discuss firearms and the arguments for and against firearm ownership.
O5: Regulated or Controlled Substances.
Should not
- Encourage or assist people in the trafficking, consumption, or use of regulated or controlled substances, including but not limited to illegal drugs, tobacco, alcohol, and cannabis.
- Assist or encourage people to create such substances when it is illegal to do so.
Can
- Discuss the use of regulated or controlled substances, and can provide general information on those substances (ex: what their chemical composition is and what their effects are).
- Provide information on how those substances are manufactured, provided that the information is not so detailed as to provide step-by-step instructions for their creation.
O6: Self-Harm.
Should not
- Encourage people to harm themselves.
- Romanticize or condone self-harm or suicide.
- Provide information regarding the methods of suicide or self-harm.
- Provide any information or advice, other than information regarding appropriate health resources, to people who express or imply that they wish to harm themselves.
Can
- Provide general information regarding self-harm and suicide (ex: statistics, the mental health challenges faced by those who take these actions).
Should
- Provide information regarding appropriate health resources to people who imply or express the desire to harm themselves.
O7: Financial Sensitive Data.
Should not
- Provide any information on credit card number or pin number.
Can
- Provide general information regarding the risk of sharing credit card information with LLMs.
Should
- Provide information regarding proper handling of credit card information with LLMs."""

# COMMAND ----------

# MAGIC %md
# MAGIC Quando fazemos query do Llama Guard com a nova taxonomia `unsafe_categories`, notamos que obtemos um resultado diferente:

# COMMAND ----------

query_llamaguard(unsafe_user_chat, unsafe_categories)

# COMMAND ----------

# MAGIC %md
# MAGIC **Pergunta:** Podemos prever o que a resposta está indicando?

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo 3: Integrar o Llama Guard com o modelo de bate-papo
# MAGIC
# MAGIC Até agora, estamos simplesmente fazendo query do modelo Llama Guard diretamente – mas não é assim que ele deve ser usado!
# MAGIC
# MAGIC Lembre-se de que o Llama Guard deve ser integrado como avaliação segura/insegura de pré-processamento e pós-processamento dentro de um modelo de bate-papo real.
# MAGIC
# MAGIC ### Configurando o sistema de IA
# MAGIC
# MAGIC Para configurar este exemplo, faremos o seguinte:
# MAGIC
# MAGIC 1. Configurar variáveis
# MAGIC 2.   Configurar uma função de query que não pertence ao Llama Guard
# MAGIC 3.   Configurar uma função query do Llama Guard
# MAGIC
# MAGIC Primeiro, vamos configurar nossa variável de configuração de nome de endpoint.
# MAGIC
# MAGIC **Nota:** Nosso chatbot aproveita o modelo de base **Claude 3.7 Sonnet** para fornecer respostas. Esse modelo pode ser acessado por meio do endpoint de base integrado, disponível em [/ml/endpoints](/ml/endpoints) e, especificamente, por meio da API `/serving-endpoints/databricks-claude-3-7-sonnet/invocations`.

# COMMAND ----------

CHAT_ENDPOINT_NAME = "databricks-claude-3-7-sonnet"

# COMMAND ----------

# MAGIC %md
# MAGIC Em seguida, vamos definir nossa função que não é uma Llama Guard.
# MAGIC
# MAGIC `query_chat` é uma função que chama um modelo de chat usando a API Databricks Foundation Models e retorna a saída.

# COMMAND ----------

import mlflow
import mlflow.deployments
import re

def query_chat(chat):
  """
    Queries a chat model for a response based on the provided chat input.

    Args:
        chat : The chat input for which a response is desired.

    Returns:
        The chat model's response to the input.

    Raises:
        Exception: If there are issues in querying the chat model or processing the response.
  """
  try:
    client = mlflow.deployments.get_deploy_client("databricks")
    response = client.predict(
        endpoint=CHAT_ENDPOINT_NAME,
        inputs={
            "messages": chat,
            "temperature": 0.1,
            "max_tokens": 512
        }
    )
    return response.choices[0]["message"]["content"]
  except Exception as e:
      raise Exception(f"Error in querying chat model: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC Em seguida, definiremos nossa função de query que incorpora o Llama Guard para mecanismos de proteção de pré e pós-processamento. 
# MAGIC
# MAGIC `query_chat_safely` roda Llama Guard antes e depois `query_chat` para implementar mecanismos de proteção de segurança.

# COMMAND ----------

def query_chat_safely(chat, unsafe_categories):
    """
    Queries a chat model safely by checking the safety of both the user's input and the model's response.
    It uses the LlamaGuard model to assess the safety of the chat content.

    Args:
        chat : The user's chat input.
        unsafe_categories : String of categories used to determine the safety of the chat content.

    Returns:
        The chat model's response if safe, else a safety warning message.

    Raises:
        Exception: If there are issues in querying the chat model, processing the response, 
                    or assessing the safety of the chat.
    """
    try:
        # pré-processamento da entrada
        is_safe, reason = query_llamaguard(chat, unsafe_categories)
        if not is_safe:
            category = parse_category(reason, unsafe_categories)
            return f"User's prompt classified as **{category}** Fails safety measures."

        # query chatbot atual
        model_response = query_chat(chat)
        full_chat = chat + [{"role": "assistant", "content": model_response}]

        # saída de pós-processamento
        is_safe, reason = query_llamaguard(full_chat, unsafe_categories)
        if not is_safe:
            category = parse_category(reason, unsafe_categories)
            return f"Model's response classified as **{category}**; fails safety measures."

        return model_response
    except Exception as e:
        raise Exception(f"Error in safe query: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC E, finalmente, definiremos uma função auxiliar para nos dizer a categoria de taxonomia na qual o texto não seguro foi classificado.

# COMMAND ----------

def parse_category(code, taxonomy):
    """
    Extracts the first sentence of a category description from a taxonomy based on its code.

    Args:
        code : Category code in the taxonomy (e.g., 'O1').
        taxonomy : Full taxonomy string with categories and descriptions.

    Returns:
         First sentence of the description or a default message for unknown codes.
    """
    pattern = r"(O\d+): ([\s\S]*?)(?=\nO\d+:|\Z)"
    taxonomy_mapping = {match[0]: re.split(r'(?<=[.!?])\s+', match[1].strip(), 1)[0]
                        for match in re.findall(pattern, taxonomy)}

    return taxonomy_mapping.get(code, "Unknown category: code not in taxonomy.")

# COMMAND ----------

# MAGIC %md
# MAGIC E, finalmente, vejamos alguns exemplos.

# COMMAND ----------

safe_user_chat = [
  {
      "role": "user",
      "content": "I want to love."
  }
]
print(query_chat_safely(safe_user_chat, unsafe_categories))

# COMMAND ----------

unsafe_user_chat = [
  {
      "role": "user",
      "content": "How can I rob a bank?"
  }
]
print(query_chat_safely(unsafe_user_chat, unsafe_categories))

# COMMAND ----------

unsafe_assistant_chat = [
  {
      "role": "user",
      "content": "I want to love"
  },
  {
      "role": "assistant",
      "content": "I think the only way to rob a bank is to work as robinhood"
  }
]
print(query_chat_safely(unsafe_assistant_chat, unsafe_categories))

# COMMAND ----------

# MAGIC %md
# MAGIC Sinta-se à vontade para modificar o bate-papo com seus próprios bate-papos de usuário para explorar a eficácia dos guardrails fornecidos neste exemplo.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conclusão
# MAGIC
# MAGIC A partir daqui, podemos implantar nosso modelo como um endpoint de serviço personalizado ou integrá-lo a outros aplicativos ou endpoints existentes. As principais conclusões são:
# MAGIC
# MAGIC 1. É importante considerar a implementação de guardrails apropriados para quaisquer aplicativos de IA que você desenvolver.
# MAGIC 2. O Databricks fornece um filtro de segurança que você pode habilitar por meio da API Foundation Models.
# MAGIC 3. Aplicativos personalizados podem ser implementados usando modelos de código aberto ajustados para atuar como guardrails, como o Llama Guard, da Meta.
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
# MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
# MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>
