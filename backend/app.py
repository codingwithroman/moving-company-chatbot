from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import QwenEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_community.llms import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

DEEPSEEK_API_BASE = "https://api.deepseek.com"

# Load and parse PDF doc
loader = PyPDFLoader("terms_conditions.pdf")
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

if not documents:
    raise ValueError("No text was extracted from the PDF")


# Create embeddings and store in vector db
embeddings = QwenEmbeddings(
    model="text-embedding-ada-002"
    qwen_api_key=
)
vector_store = FAISS.from_documents(texts, embeddings)

# Initialize DeepSeek v3
llm = OpenAI(
    openai_api_key=api_key,
    openai_api_base=DEEPSEEK_API_BASE,
    model="deepseek-chat"
)

# Set up RAG chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_store.as_retriever(),
    return_source_documents=False
)

# API endpoint simulation

def get_response(query):
    result = qa_chain({"query": query})
    return result["result"]

if __name__ == "__main__":
    query = "Wat is het annuleringsbeleid?"
    response = get_response(query)
    print(response)