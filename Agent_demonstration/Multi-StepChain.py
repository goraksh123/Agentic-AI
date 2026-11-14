#Automated Customer Review & Support Ticket Escalation System used by e-commerce companies.
#When a customer submits a low-rating review or complaint,
#  a single prompt cannot simultaneously track the sentiment,
#  translate it,
#  summarize it for the engineering team,
#  and generate a polite customer support email in the user's language without messing up details.
# A modern runnable pipeline handles this sequentially like an assembly line.

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

os.environ["GOOGLE_API_KEY"] = "AQ.Ab8RN6K4P_LWVmeSchY28Scfh6iQ3n8zc2d39aHlFbb0pwFDnw"

llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    temperature=0.7,
)


# 1. Setup API Keys & LLM
#os.environ["OPENAI_API_KEY"] = "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"
#llm = ChatOpenAI(model="gpt-4o", temperature=0)

# --- STEP 1: Sentiment & Translation ---
prompt_1 = PromptTemplate(
    input_variables=["raw_review"],
    template=(
        "Analyze the following customer review.\n"
        "1. Translate it completely into English.\n"
        "2. Identify the sentiment as either 'Positive' or 'Negative'.\n\n"
        "Review: {raw_review}\n\n"
        "Format your output exactly as:\n"
        "SENTIMENT: [Positive/Negative]\n"
        "TRANSLATION: [English text]"
    ),
)

# --- STEP 2: Issue Extraction & Summary ---
prompt_2 = PromptTemplate(
    input_variables=["processed_review"],
    template=(
        "Based on this analyzed review:\n{processed_review}\n\n"
        "Extract the exact technical or logistical issues the customer faced "
        "and summarize them into a 1-sentence summary for our engineering dashboard."
    ),
)

# --- STEP 3: Automated Support Email Response ---
prompt_3 = PromptTemplate(
    input_variables=["technical_summary", "customer_name", "language"],
    template=(
        "Draft a professional customer support email to {customer_name}.\n"
        "Acknowledge their exact issue: '{technical_summary}'.\n"
        "Assure them our team is fixing it and offer a $15 refund coupon code: REEFUND15.\n"
        "The entire email must be written natively in {language}."
    ),
)

# --- STEP 4: Runnable pipeline (modern LangChain style) ---
step_1 = prompt_1 | llm | StrOutputParser()
print("STEP 1:", step_1)

step_2 = prompt_2 | llm | StrOutputParser()
print("STEP 2:", step_2)

step_3 = prompt_3 | llm
print("STEP 3:", step_3)



# --- RUNNING THE PIPELINE ---
incoming_review = (
    "El paquete llegó con 4 días de retraso y cuando lo abrí, "
    "la pantalla del producto estaba rota. Muy insatisfecho."
)
customer = "Carlos Gomez"
reply_language = "Spanish"

processed_review = step_1.invoke({"raw_review": incoming_review})
print("Processed Review:", processed_review)

technical_summary = step_2.invoke({"processed_review": processed_review})
print("Technical Summary:", technical_summary)
print("Reply Language:", reply_language)
print("Customer Name:", customer)

support_email = step_3.invoke(
    {
        "technical_summary": technical_summary,
        "customer_name": customer,
        "language": reply_language,
    }
)

result = {
    "processed_review": processed_review,
    "technical_summary": technical_summary,
    "support_email": support_email.content,
}
print("Model Output Type:")
print(type(result))
print(result.__contains__)

# --- OUTPUT VIEW ---
print("\n=== STEP 1: Sentiment & Translation ===")
print(result["processed_review"])

print("\n=== STEP 2: Core Issue for Engineering Dashboard ===")
print(result["technical_summary"])

print("\n=== STEP 3: Drafted Support Email ===")
print(result["support_email"])
