from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# मॉडल सेटअप
llm = ChatOllama(model="gemma3:4b")

# प्रॉम्प्ट टेम्पलेट बनाएं
prompt = ChatPromptTemplate.from_messages([
    ("system", "आप एक सहायक AI हैं जो केवल हिंदी में जवाब देता है।"),
    ("user", "{topic} के बारे में एक मजेदार तथ्य बताएं।")
])

# LCEL (LangChain Expression Language) का उपयोग करके चेन बनाएं
chain = prompt | llm

# चेन को रन करें
response = chain.invoke({"topic": "MacBook"})
print(response.content)