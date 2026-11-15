
#The 3 Core Steps of a RAG Pipeline

#1. Ingestion & Embedding: Documents (PDFs, TXT files, Notion pages) are chopped into small chunks, 
# converted into numbers (vectors), and stored in a specialized Vector Database.
#2. Retrieval: The user asks a question. The system searches the vector database to find the text chunks 
# that are most similar to the question.
#3. Generation: The question and the retrieved text chunks are wrapped together in a prompt 
# 00and sent to the LLM to generate a factual answer.




import os
import uuid
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = "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"
os.environ["LANGSMITH_PROJECT"] = "ollama-gemma3-development"


#from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.chains.router import MultiPromptChain
from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser
from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import InMemoryVectorStore


from langchain_ollama import ChatOllama, OllamaEmbeddings

#import google.generativeai as genai
from RoutingAuditHandler import RoutingAuditHandler
import time
from langsmith import Client


from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


#Callbacks: Use custom callbacks to log routing decisions, execution times, and errors.
request_id = str(uuid.uuid4())
audit_handler = RoutingAuditHandler(request_id)
run_name = os.path.splitext(os.path.basename(__file__))[0]


OLLAMA_BASE_URL = "http://localhost:11434"


## 1. Setup API Keys & LLM
llm = ChatOllama(
    model="gemma3:4b",
    base_url=OLLAMA_BASE_URL,
    temperature=0
)


# Embedding model for semantic search
embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url=OLLAMA_BASE_URL
)

# =====================================================
# 2. VECTOR STORE AND DOCUMENT INGESTION
# =====================================================

vector_store = InMemoryVectorStore(
    embedding=embeddings
)


private_documents = [
    "Company Policy: Employees are allowed up to 25 days of paid annual leave.",
    "Company Policy: Remote work is permitted up to 3 days per week with manager approval.",
    "Project Apollo Status: The launch date has been rescheduled to December 12, 2026."
]

# Store documents and generate embeddings
vector_store.add_texts(private_documents)



# =====================================================
# 3. CREATE RETRIEVER
# =====================================================

retriever = vector_store.as_retriever(
    search_kwargs={"k": 2}
)



# =====================================================
# 5. RAG PROMPT TEMPLATE
# =====================================================

rag_template = """
You are a helpful company assistant.

Answer the user's question using ONLY the
provided context.

If you do not know the answer based on the
context, say:

'I cannot find that information in company records.'

Context:
{context}

Question:
{question}

Answer:
"""

prompt = ChatPromptTemplate.from_template(
    rag_template
)


chain_with_retriever = (
    {
        "context": retriever,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)


# 6. Test the RAG Chain
query = "When is the launch date for Project Apollo, and how many remote days do I get?"
response = chain_with_retriever.invoke(query)


query = "How many paid leaves are allowed?"
response = chain_with_retriever.invoke(query)



print("=== USER QUERY ===")
print(query)
print("\n=== AI RESPONSE (AUGMENTED BY PRIVATE DATA) ===")
print(response)