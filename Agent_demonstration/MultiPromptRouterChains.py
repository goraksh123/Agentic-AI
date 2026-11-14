

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.chains.router import MultiPromptChain
from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser
from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE
from langchain.prompts import PromptTemplate

from langchain_ollama import ChatOllama

import google.generativeai as genai



#LangSmith tracing: Capture every router and destination execution.
#Prompt identification: Assign a unique prompt ID and version to every template.
#Routing audit: Log the selected destination for every request.
#Correlation ID: Connect application logs with LangSmith traces.
# Error handling: Capture routing failures, invalid destinations and LLM errors.
#Evaluation: Maintain test datasets to detect incorrect routing after prompt changes.
# Security: Redact sensitive production inputs and restrict trace access.

#os.environ["GOOGLE_API_KEY"] = "AQ.Ab8RN6KqjJ0i2ZNGOdAe1BXpknsFm1-v_Spp72-ipk7HfaHSCw"

#llm = ChatGoogleGenerativeAI(
#    model="gemini-3.8-flash",
#    temperature=0.7
#)




llm = ChatOllama(model="gemma3:4b")


# 2. गंतव्य चेन्स (Destination Chains) के लिए प्रॉम्प्ट्स परिभाषित करें
math_template = """You are a brilliant mathematician. You are great at answering math questions. \
Here is a question:
{input}"""

history_template = """You are a very wise historian. You have a deep understanding of history. \
Here is a question:
{input}"""


# 3. गंतव्य चेन्स की एक लिस्ट (Infos) बनाएं
prompt_infos = [
    {
        "name": "math",
        "description": "Good for answering questions about mathematics",
        "prompt_template": math_template,
    },
    {
        "name": "history",
        "description": "Good for answering questions about history",
        "prompt_template": history_template,
    },
]



destination_chains = {}
for p_info in prompt_infos:
    name = p_info["name"]
    prompt = PromptTemplate(template=p_info["prompt_template"], input_variables=["input"])
    chain = LLMChain(llm=llm, prompt=prompt)
    destination_chains[name] = chain



# 5. एक डिफॉल्ट चेन (Default Chain) बनाएं (अगर क्वेरी किसी कैटेगरी में फिट न हो)
default_prompt = PromptTemplate(template="{input}", input_variables=["input"])
default_chain = LLMChain(llm=llm, prompt=default_prompt)


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


# 7. मुख्य MultiPromptChain (Router Chain) को असेम्बल करें
support_router_system = MultiPromptChain(
    router_chain=router_chain,
    destination_chains=destination_chains,
    default_chain=default_chain,
    verbose=True
)




#print("--- Test 1 (Technical Issue) ---")
#print(support_router_system.run("My app crashes with Error Code 502 every time I open the cart."))

#print("\n--- Test 2 (Billing Issue) ---")
#print(support_router_system.run("I was charged $45 twice on my credit card yesterday, please refund me."))

#print("\n--- Test 3 (General Query / Default) ---")
#print(support_router_system.run("What are your office operational hours during holidays?"))

print("\n--- Test 4 (General Query / Default) ---")
print(support_router_system.run("What are 4+3*5-10*134555*1000"))



