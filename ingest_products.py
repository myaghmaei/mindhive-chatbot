# ingest_products.py
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma # Import Chroma
import os
from dotenv import load_dotenv

load_dotenv()

print("Starting product ingestion with ChromaDB...")

# Use the same pre-defined list of products
products_data = [
    "Product Name: ZUS All-Purpose Tumbler (2023 Edition), Price: RM59.90",
    "Product Name: ZUS Signature Mixes - Himalayan Salt, Price: RM19.90",
    "Product Name: ZUS Signature Mixes - Chocolate, Price: RM19.90",
    "Product Name: ZUS x Sttoke Reusable Cup (12oz), Price: RM148.00",
    "Product Name: ZUS Plastic Reusable Cup (16oz), Price: RM19.90",
    "Product Name: ZUS Stainless Steel Tumbler (22oz), Price: RM89.90",
    "Product Name: ZUS Button Tumbler, Price: RM79.90"
]

print(f"Loaded {len(products_data)} products.")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
documents = text_splitter.create_documents(products_data)

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Create the ChromaDB vector store and persist it to disk
# This will create a folder named 'chroma_db_products'
vector_store = Chroma.from_documents(
    documents, 
    embeddings, 
    persist_directory="./chroma_db_products"
)

print("Product ingestion complete. ChromaDB index 'chroma_db_products' created.")