#An Agent-Based Chain (commonly referred to as an Agent) is a dynamic system 
# where the LLM does not follow a fixed, pre-determined sequence of steps. 
# Instead, the LLM acts as a "brain" that looks at a user's query, decides which tool to use, uses that tool,
# observes the result, and repeats the process until the problem is solved.
# In modern LangChain, we build agents using ReAct (Reasoning and Acting) logic. 
# The agent uses tools (like Google Search or a Calculator) to resolve a prompt dynamically.

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain, SequentialChain
from langchain.prompts import PromptTemplate
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.core.tools import tool
import google.generativeai as genai
from langchain import hub


os.environ["GOOGLE_API_KEY"] = "AQ.Ab8RN6LADv_ZpD0mbm9u2MtdHhSvne_KD4po5EhjZL4XwMaK7A"
lm = ChatGoogleGenerativeAI(
     model="gemini-3.8-flash",
    temperature=0.7
)


# 1. Setup API Keys & LLM
#os.environ["OPENAI_API_KEY"] = "your-api-key-here"
#llm = ChatOpenAI(model="gpt-4o", temperature=0)


print("\n=== FINAL ANSWER ===")
print(response["output"])


# 2. Define Custom Tools
# We can create tools easily using the @tool decorator
@tool
def calculate_word_length(word: str) -> int:
    """Returns the exact number of characters in a word."""
    return len(word)


# Let's also set up a standard Wikipedia search tool
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())


# Combine tools into a list
tools = [wikipedia, calculate_word_length]



prompt = hub.pull("hwchase17/react")
print(prompt)

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


# 5. Run the Agent with a complex, multi-step dynamic query
query = (
    "Who is the current CEO of Microsoft? "
    "Find the exact character length of their last name."
)


result = agent_executor.invoke({ "input": query})

print("\n=== FINAL ANSWER ===")
print(response["output"])