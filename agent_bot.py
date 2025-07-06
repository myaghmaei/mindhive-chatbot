# agent_bot.py

import os
from dotenv import load_dotenv
import numexpr
import requests

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import tool
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import AIMessage, HumanMessage
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents import AgentExecutor

load_dotenv()
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest", 
    temperature=0, 
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# --- 1. Define ALL The Tools (with improved error handling) ---

@tool
def calculator(expression: str) -> str:
    """Useful for when you need to answer questions about math."""
    try:
        result = numexpr.evaluate(expression).item()
        return f"The result of the expression '{expression}' is {result}."
    except Exception as e:
        return f"Sorry, I couldn't calculate that. The expression '{expression}' is not valid."

@tool
def query_outlets_api(query: str) -> str:
    """
    Useful for answering questions about ZUS Coffee outlet locations, addresses, and opening hours.
    Example: "Are there any outlets in Petaling Jaya?"
    """
    url = f"http://127.0.0.1:8000/outlets?query={query}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # **IMPROVED ERROR CHECKING**
        if "error" in data:
            return f"The API returned an error: {data['error']}"
        return data.get("response", "No response found.")
    except requests.exceptions.RequestException as e:
        return f"Error connecting to the outlets API: {e}"

@tool
def query_products_api(query: str) -> str:
    """
    Useful for answering questions about ZUS Coffee drinkware products, like tumblers and cups.
    Example: "What kind of reusable cups do you sell?"
    """
    url = f"http://127.0.0.1:8000/products?query={query}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # **IMPROVED ERROR CHECKING**
        if "error" in data:
            return f"The API returned an error: {data['error']}"
        return data.get("response", "No response found.")
    except requests.exceptions.RequestException as e:
        return f"Error connecting to the products API: {e}"

tools = [calculator, query_outlets_api, query_products_api]

# --- 2. Create the Agent and Executor (Same as before) ---
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant for ZUS Coffee."),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)
llm_with_tools = llm.bind_tools(tools)
agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
            x["intermediate_steps"]
        ),
    }
    | prompt
    | llm_with_tools
    | OpenAIToolsAgentOutputParser()
)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)


# --- Interactive Demo ---
def run_agent_demo():
    print("ZUS Coffee Super Agent is ready! Ask me about outlets, products, or math.")
    print("Type 'exit' to end.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        
        response = agent_executor.invoke({"input": user_input})
        print(f"Agent: {response['output']}")

if __name__ == '__main__':
    run_agent_demo()