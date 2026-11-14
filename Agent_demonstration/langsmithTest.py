import os
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = "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"
os.environ["LANGSMITH_PROJECT"] = "ollama-gemma3-development"


from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate


llm = ChatOllama(
    model="gemma3:4b",
    base_url="http://localhost:11434",
    temperature=0
)

response = llm.invoke(
    "Explain Java virtual threads"
)

print(response.content)