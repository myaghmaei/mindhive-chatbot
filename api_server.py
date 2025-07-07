# api_server.py

import os
import re
from dotenv import load_dotenv
from fastapi import FastAPI

# Imports for Text2SQL
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain

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

# --- Outlets Text2SQL Endpoint ---
db = SQLDatabase.from_uri("sqlite:///zus_outlets.db")
sql_query_chain = create_sql_query_chain(llm, db)

@app.get("/outlets")
def get_outlet_info(query: str):
    try:
        raw_sql_query = sql_query_chain.invoke({"question": query})
        sql_match = re.search(r"SELECT.*", raw_sql_query, re.IGNORECASE | re.DOTALL)
        if not sql_match:
            raise ValueError("Failed to generate a valid SQL query.")
        sql_query = sql_match.group(0).strip()
        if not sql_query.upper().startswith("SELECT"):
             raise ValueError("Only SELECT queries are allowed.")
        result = db.run(sql_query)
        return {"response": str(result)}
    except Exception as e:
        return {"error": str(e)}

# --- Products RAG Endpoint (SIMPLIFIED) ---
# Hardcode the product data directly. No vector store needed for this small dataset.
products_data = [
    "Product Name: ZUS All-Purpose Tumbler (2023 Edition), Price: RM59.90",
    "Product Name: ZUS Signature Mixes - Himalayan Salt, Price: RM19.90",
    "Product Name: ZUS Signature Mixes - Chocolate, Price: RM19.90",
    "Product Name: ZUS x Sttoke Reusable Cup (12oz), Price: RM148.00",
    "Product Name: ZUS Plastic Reusable Cup (16oz), Price: RM19.90",
    "Product Name: ZUS Stainless Steel Tumbler (22oz), Price: RM89.90",
    "Product Name: ZUS Button Tumbler, Price: RM79.90"
]
# Join the list into a single string of context
product_context = "\n".join(products_data)

@app.get("/products")
async def get_product_info(query: str):
    """
    Answers questions about ZUS Coffee drinkware products using a simplified RAG approach.
    """
    # Create the prompt on-the-fly with the full context
    prompt = f"""You are a helpful ZUS Coffee assistant. Answer the user's question based only on the following product list:

    {product_context}

    Question: {query}
    """
    try:
        response = llm.invoke(prompt)
        return {"response": response.content}
    except Exception as e:
        return {"error": str(e)}

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "ZUS Coffee API is running."}