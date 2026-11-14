import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain, SequentialChain
from langchain.prompts import PromptTemplate

import google.generativeai as genai

os.environ["GOOGLE_API_KEY"] = "AQ.Ab8RN6KqjJ0i2ZNGOdAe1BXpknsFm1-v_Spp72-ipk7HfaHSCw"

llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    temperature=0.7
)



prompt_1 = PromptTemplate(
    input_variables=["review"],
    template="Translate the following review into English:\n\n{review}"
)
chain_one = LLMChain(llm=llm, prompt=prompt_1, output_key="english_review")



prompt_2 = PromptTemplate(
    input_variables=["english_review"],
    template="Summarize the following review in one sentence:\n\n{english_review}"
)
chain_two = LLMChain(llm=llm, prompt=prompt_2, output_key="summary")


prompt_3 = PromptTemplate(
    input_variables=["summary", "language"],
    template="Write a customer service reply to this summary: '{summary}'. The reply must be written in {language}."
)


chain_three = LLMChain(llm=llm, prompt=prompt_3, output_key="reply")




complex_sequential_chain = SequentialChain(chains=[chain_one, chain_two, chain_three],
 verbose=True,input_variables=["review", "language"],output_variables=["english_review", "summary",  "reply"])


#complex_sequential_chain = SimpleSequentialChain(
#    chains=[chain_one, chain_two, chain_three],
#    verbose=True
#)

user_review = "Ce produit est absolument fantastique, mais la livraison a été très lente." # फ्रेंच रिव्यू
chosen_lang = "Hindi"

result = complex_sequential_chain({"review": user_review, "language": chosen_lang})

print("--- ENGLISH Review ---")
print(result["english_review"])
print("--- Summary ---")
print(result["summary"])
print("--- Customer Service Reply ---")
print(result["reply"])


