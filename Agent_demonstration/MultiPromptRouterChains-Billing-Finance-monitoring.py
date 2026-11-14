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
from langchain_ollama import ChatOllama
#import google.generativeai as genai
from RoutingAuditHandler import RoutingAuditHandler
import time
from langsmith import Client



#LangSmith tracing: Capture every router and destination execution.
#Prompt identification: Assign a unique prompt ID and version to every template.
#Routing audit: Log the selected destination for every request.
#Correlation ID: Connect application logs with LangSmith traces.
#Error handling: Capture routing failures, invalid destinations and LLM errors.
#Evaluation: Maintain test datasets to detect incorrect routing after prompt changes.
#Security: Redact sensitive production inputs and restrict trace access.
#Callbacks: Use custom callbacks to log routing decisions, execution times, and errors.


#Your main objective should be to answer these questions for every incoming request:
#1. Which router prompt was executed?
#2. What routing decision did the LLM make?
#3. Which destination chain was selected (math, history, etc.)?
#4. Which exact PromptTemplate was used?
#5. What was the final prompt sent to the LLM?
#6. How long did routing and destination execution take?
#7. Did the router select the wrong destination or fall back to the default chain?





#Callbacks: Use custom callbacks to log routing decisions, execution times, and errors.
request_id = str(uuid.uuid4())
audit_handler = RoutingAuditHandler(request_id)
run_name = os.path.splitext(os.path.basename(__file__))[0]


## 1. Setup API Keys & LLM
llm = ChatOllama(
    model="gemma3:4b",
    base_url="http://localhost:11434",
    temperature=0
)


# 2. अलग-अलग विभागों (Destination Chains) के लिए प्रॉम्प्ट्स
tech_template = """You are a Senior Technical Support Engineer. Your job is to provide step-by-step \
troubleshooting instructions for app errors, bugs, or hardware issues. Keep your tone professional.
Customer Issue:
{input}"""

billing_template = """You are a Corporate Billing and Finance Expert. Your job is to answer questions \
regarding invoice discrepancies, subscription renewals, or refund status based on company policy.
Customer Issue:
{input}"""

# 3. गंतव्य चेन्स की एक लिस्ट (Infos) बनाएं
prompt_infos = [
    {
        "name": "tech",
        "description": "Good for answering technical support questions",
        "prompt_template": tech_template,
        "prompt_id": "tech_prompt",
        "prompt_version": "v1"
    },
    {
        "name": "billing",
        "description": "Good for answering billing and finance questions",
        "prompt_template": billing_template,
        "prompt_id": "billing_prompt",
        "prompt_version": "v1"
    }
]



destination_chains = {}
for p_info in prompt_infos:
    name = p_info["name"]
    prompt = PromptTemplate(template=p_info["prompt_template"], input_variables=["input"])
    chain = LLMChain(llm=llm, prompt=prompt, metadata={
        "prompt_id": p_info["prompt_id"], 
        "prompt_version": p_info["prompt_version"],
        "destination_name": name})
    destination_chains[name] = chain



# 5. एक डिफॉल्ट चेन (Default Chain) बनाएं (अगर क्वेरी किसी कैटेगरी में फिट न हो)
default_prompt = PromptTemplate(template="{input}", input_variables=["input"])
default_chain = LLMChain(llm=llm, prompt=default_prompt, metadata={
    "prompt_id": "default_prompt",
    "prompt_version": "v1",
    "destination_name": "default"
})


# 6. राउटर प्रॉम्प्ट (Router Prompt) और राउटर चेन तैयार करें
destinations = [f"{p['name']}: {p['description']}" for p in prompt_infos]
destinations_str = "\n".join(destinations)

print("=== Destinations ===")
print(destinations_str)


router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(destinations=destinations_str)
router_prompt = PromptTemplate(
    template=router_template,
    input_variables=["input"],
    output_parser=RouterOutputParser(),
)
router_chain = LLMRouterChain.from_llm(llm, router_prompt)
router_chain.metadata = {
    "prompt_id": "router_prompt",
    "prompt_version": "v1",
    "destination_name": "router"
}

# 7. मुख्य MultiPromptChain (Router Chain) को असेम्बल करें
support_router_system = MultiPromptChain(
    router_chain=router_chain,
    destination_chains=destination_chains,
    default_chain=default_chain,
    verbose=True
)

def run_router_query(question: str, request_id_value: str = None):
    current_request_id = request_id_value or str(uuid.uuid4())
    current_handler = RoutingAuditHandler(current_request_id)

    print(f"\n--- Running query: {question} ---")
    result = support_router_system.invoke(
        {"input": question},
        config={
            "callbacks": [current_handler],
            "run_name": run_name,
            "tags": [
                "production-debug",
                "gemma3-4b"
            ],
            "metadata": {
                "request_id": current_request_id,
                "environment": "development"
            }
        }
    )
    print(result)
    return result


# Example usage:
run_router_query("My app crashes with Error Code 502 every time I open the cart.")
run_router_query("I was charged $45 twice on my credit card yesterday, please refund me.")
run_router_query("What are your office operational hours during holidays?")

print("Finishing execution... forcing LangSmith trace sync...")
client = Client()
client.flush()
time.sleep(2)
print("Done!")





