# conversation_bot.py

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.memory import ConversationBufferMemory

# Load environment variables from .env file (for the API key)
load_dotenv()

# 1. Initialize the LLM (Language Model)
# We use ChatOpenAI, but this could be any LangChain-compatible chat model.
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

# 2. Set up Memory
# This is the core of Part 1. It stores the conversation history.
# `memory_key="chat_history"` means the conversation history will be available
# in our prompt template under the variable name "chat_history".
# `return_messages=True` ensures the memory returns `ChatMessage` objects
# that the prompt template can understand.
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# 3. Create the Prompt Template
# This template instructs the LLM on how to behave and structures the input.
prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(
            "You are a helpful assistant for ZUS Coffee. Answer the user's questions based on the conversation history."
        ),
        # The `MessagesPlaceholder` is where the memory is injected.
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{question}")
    ]
)

# 4. Create the LLMChain
# This "chain" ties the LLM, prompt, and memory together.
# `verbose=True` lets us see the thinking process in the terminal.
conversation_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=memory,
    verbose=True
)


# --- Interactive Demo ---
def run_demo():
    print("Chatbot is ready! Type 'exit' to end the conversation.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        
        # This is where the magic happens. The chain takes the input,
        # gets the history from memory, formats the prompt, sends it to the LLM,
        # gets the response, and stores the new turn back into memory.
        response = conversation_chain.predict(question=user_input)
        print(f"Bot: {response}")

if __name__ == '__main__':
    run_demo()
