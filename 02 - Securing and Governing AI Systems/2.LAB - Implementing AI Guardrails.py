# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">
# MAGIC </div>
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC #Lab 2: Implementação de barreiras de proteção de IA
# MAGIC
# MAGIC Neste laboratório, você implementará guardrails para uma aplicação de GenAI simples para protegê-la contra comportamento mal-intencionado e saída gerada prejudicial.
# MAGIC
# MAGIC
# MAGIC **Esboço do laboratório:**
# MAGIC
# MAGIC Neste laboratório, você precisará concluir as seguintes tarefas:
# MAGIC
# MAGIC * **Tarefa 1:** Implementar guardrails baseados em LLM com o modelo Llama Guard.
# MAGIC   1. Configurar o modelo do Llama Guard e as variáveis de configuração
# MAGIC   2. Implementar a função query_llamaguard
# MAGIC   3. Testar a implementação
# MAGIC * **Tarefa 2:** Personalizar guardrails do Llama Guard
# MAGIC   1. Definir categorias não seguras personalizadas
# MAGIC   2. Testar a implementação
# MAGIC * **Tarefa 3:** Integrar o Llama Guard com o Modelo de Chat
# MAGIC   1.   Configurar uma função de query que não pertence ao Llama Guard
# MAGIC   2.   Configurar uma função query do Llama Guard
# MAGIC   3. Testar a implementação

# COMMAND ----------

# MAGIC %md
# MAGIC ## Requisitos
# MAGIC
# MAGIC Por favor, revise os seguintes requisitos antes de iniciar a lição:
# MAGIC
# MAGIC * Para executar este Notebook, você precisa usar um dos seguintes tempos de execução do Databricks: **15.4.x-cpu-ml-scala2.12**

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuração da Sala de aula
# MAGIC Antes de iniciar o laboratório, execute o script de configuração de sala de aula fornecido para instalar as bibliotecas necessárias e configurar as variáveis necessárias.
# MAGIC

# COMMAND ----------

# MAGIC %pip install -U -qq databricks-sdk
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %run ../Includes/Classroom-Setup-02

# COMMAND ----------

# MAGIC %md
# MAGIC ##Tarefa 1: Implemente Guardrails baseados em LLM com `Llama Guard`
# MAGIC Primeiro, para configurar as medidas de segurança do seu aplicativo, você integrará o Llama Guard, um modelo especializado disponível no Databricks Marketplace. Isso permitirá que você classifique o conteúdo do bate-papo como seguro ou inseguro, permitindo um gerenciamento mais eficaz de interações potencialmente prejudiciais.
# MAGIC
# MAGIC
# MAGIC **Llama Guard no Databricks**
# MAGIC
# MAGIC Para agilizar o processo de integração e aproveitar os benefícios do Llama Guard, uma implantação desse modelo está prontamente disponível no Databricks Marketplace.
# MAGIC
# MAGIC **Instruções (a serem executadas apenas pelo instrutor):**
# MAGIC
# MAGIC 1. Encontre o "Llama Guard Model" em **Databricks Marketplace**.
# MAGIC 2. Clique em **Obter acesso instantâneo** para carregá-lo em um local no Unity Catalog.
# MAGIC 3. **Implante o modelo** em um Model Serving Endpoint.
# MAGIC
# MAGIC Ao integrar o Model Serving Endpoint em seu próprio aplicativo, você ganha a flexibilidade de especificar suas próprias políticas para detectar e impedir vários tipos de conteúdo. Isso garante que seu aplicativo mantenha um ambiente seguro para os usuários.
# MAGIC
# MAGIC ** Aviso:** Evite implantar o modelo por conta própria, pois pode levar tempo e pode não ser prático em um ambiente de sala de aula. Em vez disso, utilize o modelo que foi fornecido para este laboratório. Para alunos autônomos, você pode seguir as etapas acima para criar o endpoint.
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC **Instruções:**
# MAGIC 1. **Configurar o modelo do Llama Guard e as variáveis de configuração**
# MAGIC
# MAGIC     Configure uma descrição do ponto de partida da sua categoria **Inseguro**:
# MAGIC
# MAGIC     * **Para fazer:**
# MAGIC     
# MAGIC         Foram fornecidas a você 2 categorias. Sua tarefa é escrever descrições para 3 categorias adicionais com base em temas ou tópicos comuns. 
# MAGIC
# MAGIC     
# MAGIC         **Dica:** Você pode usar o AI Playground para gerar descrições para essas categorias, garantindo que elas sejam relevantes e distintas dos exemplos fornecidos.

# COMMAND ----------

DEFAULT_UNSAFE_CATEGORY = """O1: Unsafe Content.
    - Promoting or assisting in violence or hate.
    - Engaging in or encouraging sexually explicit content.
    <FILL_IN>
    """

# COMMAND ----------

# MAGIC %md
# MAGIC Defina as variáveis necessárias e configure o modelo **Llama Guard**.

# COMMAND ----------

# Nome do endpoint llama-guard. Altere isso para seu próprio nome de endpoint, se você criar um manualmente!
LLAMAGUARD_ENDPOINT_NAME="llama-guard"

# COMMAND ----------

# MAGIC %md
# MAGIC 2. **Implementar a função `query_llamaguard`**
# MAGIC
# MAGIC Desenvolva uma função para query do modelo do Llama Guard e classificar o conteúdo do bate-papo como seguro ou inseguro.

# COMMAND ----------

from databricks.sdk import WorkspaceClient

def query_llamaguard(chat, unsafe_categories = DEFAULT_UNSAFE_CATEGORY):
    try:
        prompt = <FILL_IN>
#
        w = WorkspaceClient()
        response = w.<FILL_IN>
        
        # Extraia a informação desejada do objeto de resposta
        prediction = response.as_dict()["choices"][0]["text"].strip()
        is_safe = None if len(prediction.split("\n")) == 1 else prediction.split("\n")[1].strip()
        
        return prediction.split("\n")[0].lower()=="safe", is_safe
    
    except Exception as e:
        # Gerar exceção se houver um erro ao fazer query do modelo do LlamaGuard
        raise Exception(f"Error in querying LlamaGuard model: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC 3. **Teste a implementação**
# MAGIC
# MAGIC Execute o código e teste a função `query_llamaguard` para ver se ela identifica corretamente o conteúdo não seguro.

# COMMAND ----------

##Define as entradas do chat
bate-papos = [
  {
      <FILL_IN>
  },
  {
      <FILL_IN>
  },
  {
      <FILL_IN>
  }
]

# Query da Llama Guard para vários bate-papos
result = query_llamaguard(chats, DEFAULT_UNSAFE_CATEGORY)

# Imprimir o resultado
print(result)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Tarefa 2: Personalizar as barreiras de proteção do Llama Guard
# MAGIC
# MAGIC Nesta tarefa, você personalizará os guardrails fornecidos pelo Llama Guard definindo categorias inseguras personalizadas. Isso permitirá que você adapte os critérios de avaliação de segurança para atender a requisitos específicos.
# MAGIC
# MAGIC **Instruções:**
# MAGIC 1. **Definir guardrails de categorias inseguras personalizadas**
# MAGIC
# MAGIC Defina categorias inseguras personalizadas que reflitam as preocupações de segurança específicas do seu aplicativo.

# COMMAND ----------

# Definir categorias inseguras personalizadas
unsafe_categories = """
O1: Violence and Hate.
Should not
- Promote or incite physical harm or violence against individuals or groups.
- Advocate for or glorify acts of terrorism, war crimes, or violent extremism.
- Use or promote language that denigrates individuals based on race, ethnicity, religion, gender, sexual orientation, or other protected characteristics.
Can
- Provide educational content on the history and impact of violence and hate.
- Discuss non-violent conflict resolution strategies and the importance of tolerance and inclusivity.

O2: Sexual Content.
Should not
- Share explicit, graphic, or sexually suggestive content.
- Encourage or solicit participation in sexual activities or online sexual exploitation.
Can
- Offer medically accurate information on sexual health and reproductive education.
- Discuss issues related to consent, relationships, and safe sexual practices.

O3: Criminal Planning.
Should not
- Give instructions or advice on committing crimes such as theft, hacking, or financial fraud.
- Provide resources or support for organizing criminal activities.
Can
- Explain the legal and social consequences of criminal behavior.
- Offer insights into crime prevention and law enforcement practices.

O4: Weapons and Firearms.
Should not
- Instruct on the creation, modification, or use of firearms, explosives, or other dangerous weapons.
- Promote the illegal trade or misuse of weapons.
Can
- Discuss the history and regulations surrounding weapon ownership and use.
- Provide safety information related to responsible weapon handling and storage.

O5: Controlled Substances.
Should not
- Endorse or facilitate the illegal production, sale, or consumption of drugs, alcohol, or tobacco.
- Offer recipes or detailed instructions for creating illegal substances.
Can
- Share facts on the health impacts of substance use and abuse.
- Provide information on treatment options and resources for addiction recovery.

O6: Self-Harm and Suicide.
Should not
- Promote or glorify self-harm, suicide, or other forms of self-injury.
- Describe methods or provide encouragement to engage in self-destructive behaviors.
Can
- Discuss the importance of mental health and strategies for coping with stress and emotional challenges.
- Offer information on where to find professional help and support services.

O7: Personal and Financial Information.
Should not
- Request or disseminate sensitive personal information such as Social Security numbers, bank account details, or passwords.
- Facilitate identity theft or financial fraud.
Can
- Educate on the importance of protecting personal information and online privacy.
- Share tips on recognizing and avoiding scams and fraudulent activities.
"""

# COMMAND ----------

# MAGIC %md
# MAGIC 2. **Teste a implementação**
# MAGIC
# MAGIC Query o modelo do Llama Guard com suas categorias inseguras personalizadas para ver se ele identifica corretamente o conteúdo não seguro.
# MAGIC
# MAGIC

# COMMAND ----------

#Query modelo Llama Guard com categorias personalizadas inseguras
query_llamaguard(<FILL_IN>)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Tarefa 3: Integrar o Llama Guard com o modelo de bate-papo
# MAGIC
# MAGIC Integre o Llama Guard com o modelo de bate-papo para garantir interações seguras entre os usuários e o sistema de IA. Você definirá duas funções: `query_chat` e `query_chat_safely`.
# MAGIC
# MAGIC Primeiro, vamos configurar a variável de configuração de nome de endpoint.
# MAGIC
# MAGIC **Nota:** O chatbot aproveita o modelo de base **Claude 3.7 Sonnet** para fornecer respostas. Esse modelo pode ser acessado por meio do endpoint de base integrado, disponível em [/ml/endpoints](/ml/endpoints) e, especificamente, por meio da API `/serving-endpoints/databricks-claude-3-7-sonnet/invocations`.

# COMMAND ----------

import mlflow
import mlflow.deployments
import re

CHAT_ENDPOINT_NAME = "databricks-claude-3-7-sonnet"

# COMMAND ----------

# MAGIC %md
# MAGIC **Instruções:**
# MAGIC
# MAGIC 1. **Configurar uma função de query que não é da Llama Guard** 
# MAGIC - **1.1 - Função: `query_chat`**
# MAGIC
# MAGIC     A função `query_chat` faz query do modelo de bate-papo diretamente sem aplicar os guardrails do Llama Guard.

# COMMAND ----------

def query_chat(chats):
    try:
        # Obtenha o cliente de implantação do MLflow
        client = mlflow.deployments.get_deploy_client("databricks")
        # Query o modelo de chat
        response = client.predict(
            endpoint=<FILL_IN>,
            inputs={
                "messages": <FILL_IN>,
                "temperature": 0.1,
                "max_tokens": 512
            }
        )
        # Extrair e retornar o conteúdo da resposta
        return <FILL_IN>
    except Exception as e:
        # Gerar exceção se houver um erro ao fazer query do modelo de bate-papo
        raise Exception(f"Error in querying chat model: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC 2. **Configurar uma função de query do Llama Guard**
# MAGIC
# MAGIC
# MAGIC   - **2.1 - Função: `query_chat_safely`**
# MAGIC
# MAGIC     A função `query_chat_safely` garante a aplicação de guardrails Llama Guard antes e depois de fazer query do modelo de chat. Ele avalia a entrada do usuário e a resposta do modelo em termos de segurança antes de processar mais adiante.

# COMMAND ----------

def query_chat_safely(chats, unsafe_categories):
    results = []
    try:
        # Iterar sobre cada entrada de bate-papo
        for idx, chat in enumerate(chats):
            # Pré-processar a entrada com Llama Guard
            unsafe_check = query_llamaguard([chat], unsafe_categories)
            is_safe, reason = <FILL_IN>
            
            # Se a entrada for classificada como não segura, acrescente o motivo e a categoria à lista de resultados
            if not is_safe:
                category = parse_category(<FILL_IN>)
                results.append(f"Input {idx + 1}: User's prompt classified as unsafe. Fails safety measures. Reason: {reason} - {category}")
                continue

            # Query o modelo de chat
            model_response = query_chat([<FILL_IN>])
            full_chat = [<FILL_IN>] + [{<FILL_IN>}]

            # Pós-processamento de saída com Llama Guard
            unsafe_check = <FILL_IN>
            is_safe, reason = <FILL_IN>
            
            # Se a resposta do modelo for classificada como insegura, acrescente o motivo e a categoria à lista de resultados
            if not is_safe:
                category = parse_category(<FILL_IN>)
                results.append(f"Input {idx + 1}: Model's response classified as unsafe; fails safety measures. Reason: {reason} - {category}")
                continue

            # Append a resposta do modelo à lista de resultados
            results.append(f"Input {idx + 1}: <FILL_IN>")
        return results
    except Exception as e:
        # Gerar exceção se houver um erro na query segura
        raise Exception(f"Error in safe query: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC   - **2.2 - Função: `parse_category`**
# MAGIC
# MAGIC     Esta função extrai a primeira frase de uma descrição de categoria de uma taxonomia baseada em seu código. É usado dentro da função `query_chat_safely` para fornecer uma razão mais compreensível para classificações inseguras.
# MAGIC
# MAGIC
# MAGIC
# MAGIC
# MAGIC

# COMMAND ----------

def parse_category(code, taxonomy):
    # Defina o padrão para corresponder a códigos de categoria e descrições
    pattern = r"(O\d+): ([\s\S]*?)(?=\nO\d+:|\Z)"
    
    # Crie um dicionário mapeando códigos de categoria para suas descrições
    taxonomy_mapping = {
        match[0]: re.split(r'(?<=[.!?])\s+', match[1].strip(), 1)[0]
        for match in re.findall(pattern, taxonomy)
    }

    # Retorne a descrição do código fornecido ou uma mensagem default se o código não for encontrado
    return taxonomy_mapping.get(code, "Unknown category: code not in taxonomy.")

# COMMAND ----------

# MAGIC %md
# MAGIC 3. **Teste a implementação**
# MAGIC
# MAGIC Defina as entradas de bate-papo de teste e teste a função `query_chat_safely` com essas entradas e as categorias não seguras fornecidas para verificar seu comportamento.
# MAGIC

# COMMAND ----------

# Defina as entradas do chat
chats = [
  {
      <FILL_IN>
  },
  {
      <FILL_IN>
  },
  {
      <FILL_IN>
  }
]
# Imprima os resultados
results = <FILL_IN>
for result in results:
    <FILL_IN>

# COMMAND ----------

# MAGIC %md
# MAGIC #Conclusão
# MAGIC Neste laboratório, você personalizou com sucesso os guardrails de nosso aplicativo de IA usando o Llama Guard, definindo categorias inseguras personalizadas. Essas personalizações nos permitem adaptar os critérios de avaliação de segurança aos requisitos específicos de nossa aplicação, aumentando assim a eficácia de nossos guardrails de IA na identificação e mitigação de riscos potenciais associados à geração de conteúdo prejudicial.

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
# MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
# MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>
