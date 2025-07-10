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
# MAGIC
# MAGIC
# MAGIC ## Avaliação e Governação da GenAI
# MAGIC  
# MAGIC Este curso apresenta aos alunos a avaliação e a governação de sistemas de inteligência artificial (IA) generativa. Em primeiro lugar, os alunos irão explorar o significado e a motivação por detrás da construção de sistemas de avaliação e de governação/segurança. Em seguida, os alunos serão apresentados a uma variedade de técnicas de avaliação para LLMs e as suas tarefas. Em seguida, o curso irá discutir como governar e proteger os sistemas de IA utilizando Databricks. E, por fim, o curso será concluído com uma análise da avaliação de sistemas de IA completos em relação ao desempenho e ao custo.
# MAGIC
# MAGIC ---
# MAGIC ## Pré-requisitos
# MAGIC O conteúdo foi desenvolvido para participantes com as seguintes competências/conhecimentos/capacidades:
# MAGIC - Familiaridade com conceitos de processamento de linguagem natural
# MAGIC - Familiaridade com a engenharia de prompts/melhores práticas de engenharia de prompts
# MAGIC - Familiaridade com a Databricks Data Intelligence Platform
# MAGIC - Familiaridade com RAG (preparação de dados, construção de uma arquitetura RAG, conceitos como incorporação, vectors, bases de dados vectors, etc.)
# MAGIC - Experiência na construção de aplicações **`LLM`** utilizando cadeias e agentes de raciocínio multi-estágio **`LLM`**
# MAGIC
# MAGIC ---
# MAGIC ## Programa do Curso
# MAGIC Os módulos que se seguem fazem parte do curso **Avaliação e Governação da GenAI** da **Databricks Academy**.
# MAGIC
# MAGIC
# MAGIC | Módulo | Aulas|
# MAGIC |:----:|-------|
# MAGIC | **[Legalidade de Dados e Diretrizes de segurança]($./01 - Data Legality and Guardrails)** | **Palestra -** Por que avaliar aplicativos <br> de GenAI[Demonstração: Explore o licenciamento de dataset]($./01 - Data Legality and Guardrails/1.1 - Explore Licensing of Datasets) <br>[Demo: Noções básicas de comandos e diretrizes de segurança]($./01 - Data Legality and Guardrails/1.2 - Prompts and Guardrails Basics) <br> [Lab: Implementar e testar diretrizes de segurança para LLMs]($./01 - Data Legality and Guardrails/1.LAB - Implement and Test Guardrails for LLMs)|
# MAGIC | **[Protegendo e governando sistemas de IA]($./02 - Securing and Governing AI Systems)** | **Palestra -** Segurança do Sistema de IA </br> [Demo: Implementando proteções de IA]($./02 - Securing and Governing AI Systems/2.1 - Implementing AI Guardrails) </br> [Lab: Implementando proteções de IA]($./02 - Securing and Governing AI Systems/2.LAB - Implementing AI Guardrails) | 
# MAGIC | **[Técnicas de Avaliação de GenAI]($./03 - Gen AI Evaluation Techniques)** | **Palestra -** Técnicas de Avaliação </br> [Demo: Avaliação de Benchmark]($./03 - Gen AI Evaluation Techniques/3.1 - Benchmark Evaluation) </br> [Demo: LLM-as-a-Judge]($./03 - Gen AI Evaluation Techniques/3.2 - LLM-as-a-Judge) </br> [Lab: Avaliação Específica de Domínio]($./03 - Gen AI Evaluation Techniques/3.LAB - Domain-Specific Evaluation)|
# MAGIC | **[Avaliação de aplicativos de ponta a ponta]($./04 - End-to-end Application Evaluation)** | **Palestra -** Avaliação </br>  de aplicativos de ponta a ponta[Demonstração: Avaliação com Mosaic AI Agent Evaluation]($./04 - End-to-end Application Evaluation/4.1 - Evaluation with Mosaic AI Agent Evaluation) </br>[Lab: Avaliação com Mosaic AI Agent Evaluation]($./04 - End-to-end Application Evaluation/4.LAB - Evaluation with Mosaic AI Agent Evaluation)|
# MAGIC ---
# MAGIC
# MAGIC
# MAGIC ## Requisitos
# MAGIC
# MAGIC Por favor, revise os seguintes requisitos antes de iniciar a lição:
# MAGIC
# MAGIC * Para executar notebooks de demonstração e laboratório, você precisa usar um dos seguintes tempos de execução do Databricks: **15.4.x-cpu-ml-scala2.12**

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
# MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
# MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>
