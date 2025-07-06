# api_server.py

import os
import re
from dotenv import load_dotenv
from fastapi import FastAPI

# Imports for Text2SQL
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain

# Imports for RAG
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain

# General LLM
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
app = FastAPI(
    title="ZUS Coffee Assistant API",
    description="APIs for retrieving information about ZUS Coffee products and outlets."
)
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# --- Outlets Text2SQL Endpoint (SIMPLIFIED) ---
db = SQLDatabase.from_uri("sqlite:///zus_outlets.db")
sql_query_chain = create_sql_query_chain(llm, db)

@app.get("/outlets")
def get_outlet_info(query: str):
    """
    Takes a natural language query about outlets, converts it to SQL,
    executes it, and returns the raw database result.
    """
    try:
        raw_sql_query = sql_query_chain.invoke({"question": query})
        sql_match = re.search(r"SELECT.*", raw_sql_query, re.IGNORECASE | re.DOTALL)
        
        if not sql_match:
            raise ValueError("Failed to generate a valid SQL query.")
        
        sql_query = sql_match.group(0).strip()
        if not sql_query.upper().startswith("SELECT"):
             raise ValueError("Only SELECT queries are allowed.")
        
        # Execute the query and return the RAW result directly.
        # The agent is responsible for interpreting this result for the user.
        result = db.run(sql_query)
        return {"response": str(result)}

    except Exception as e:
        return {"error": str(e)}

# --- Products RAG Endpoint (from previous step) ---
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
vector_store = FAISS.load_local("faiss_index_products", embeddings, allow_dangerous_deserialization=True)
retriever = vector_store.as_retriever()
rag_prompt = ChatPromptTemplate.from_template(
    """Answer the following question based only on the provided context:
    <context>{context}</context>
    Question: {input}"""
)
document_chain = create_stuff_documents_chain(llm, rag_prompt)
retrieval_chain = create_retrieval_chain(retriever, document_chain)

@app.get("/products")
async def get_product_info(query: str):
    try:
        response = await retrieval_chain.ainvoke({"input": query})
        return {"response": response["answer"]}
    except Exception as e:
        return {"error": str(e)}

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "ZUS Coffee API is running."}