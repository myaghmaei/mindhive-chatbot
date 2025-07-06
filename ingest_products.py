# ingest_products.py
# ingest_products.py
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
import os
from dotenv import load_dotenv

load_dotenv()

print("Starting product ingestion...")

# 1. Use a pre-defined list of products instead of scraping
# This makes our ingestion process reliable and immune to website changes.
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

# 2. Split the text into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
documents = text_splitter.create_documents(products_data)

# 3. Create embeddings and store in FAISS
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Create the vector store from the documents and save it locally
vector_store = FAISS.from_documents(documents, embeddings)
vector_store.save_local("faiss_index_products")

print("Product ingestion complete. FAISS index 'faiss_index_products' created.")