from fastapi import FastAPI, Request
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

app = FastAPI()


# --- Vector store setup ---

# Initialize Pinecone client
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "finance-assistant-index"

# Create index if it doesn't exist
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

# Connect to existing Pinecone index
index = pc.Index(index_name)

# Embedding model for text representation
embedder = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

# LangChain-compatible vector store
vector_store = PineconeVectorStore(index=index, embedding=embedder, text_key="text")

# --- Endpoint ---

@app.post("/retrieve")
async def retrieve(req: Request):
    """
    Accepts a JSON body with 'query' and returns top-k semantically similar documents.
    
    Request:
    {
        "query": "e.g. What is Apple's recent earnings performance?"
    }

    Response:
    {
        "results": [<top 3 matching document contents>]
    }
    """
    body = await req.json()
    query = body.get("query", "")
    results = vector_store.similarity_search(query, k=3)
    return {"results": [doc.page_content for doc in results]}
