import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.prompts import PromptTemplate

import google.generativeai as genai

os.environ["GOOGLE_API_KEY"] = "AQ.Ab8RN6KqjJ0i2ZNGOdAe1BXpknsFm1-v_Spp72-ipk7HfaHSCw"
llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    temperature=0.7
)
prompt_template = PromptTemplate(
    input_variables=["product"],
    template="What is a good name for a company that makes {product}?"
)
first_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="company_name")

prompt_template2 = PromptTemplate(
    input_variables=["company_name"],
    template="Write a short description for a company named {company_name}."
)
second_chain = LLMChain(llm=llm, prompt=prompt_template2)

overall_chain = SimpleSequentialChain(chains=[first_chain, second_chain], verbose=True)

# SimpleSequentialChain accepts one input for the first chain only.
result = overall_chain.run("colorful socks")
print(result)




