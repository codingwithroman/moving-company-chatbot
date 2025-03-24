from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from typing import Any, List, Mapping, Optional, Dict
from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import os

load_dotenv()
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
qwen_api_key = os.getenv("QWEN_API_KEY")
if not qwen_api_key or not deepseek_api_key:
    raise ValueError("Missing API Keys! Check .env file.")

DEEPSEEK_API_BASE = "https://api.deepseek.com"

# Custom Qwen Embeddings class
class QwenEmbeddings(Embeddings):
    def __init__(self, api_key, base_url, model="text-embedding-v3"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
    
    def embed_documents(self, texts):
        """Embed search documents."""
        embeddings = []
        for text in texts:
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
                encoding_format="float"
            )
            embedding = response.data[0].embedding
            embeddings.append(embedding)
        return embeddings
    
    def embed_query(self, text):
        """Embed query text."""
        response = self.client.embeddings.create(
            model=self.model,
            input=text,
            encoding_format="float"
        )
        return response.data[0].embedding

# Custom DeepSeek LLM class
class DeepSeekLLM(LLM):
    api_key: str
    api_base: str
    model_name: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 1024
    
    @property
    def _llm_type(self) -> str:
        return "deepseek"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs
    ) -> str:
        # Create client on demand
        client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base
        )
        
        # Format the message for the chat endpoint
        messages = [{"role": "user", "content": prompt}]
        
        response = client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stop=stop,
            **kwargs
        )
        
        return response.choices[0].message.content

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

# Load and parse PDF doc
loader = PyPDFLoader("terms_conditions.pdf")
documents = loader.load()
if not documents:
    raise ValueError("No text was extracted from the PDF")

# Convert text to chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)
if not texts:
    raise ValueError("No text chunks generated.")

# Initialize our custom Qwen embeddings
qwen_embeddings = QwenEmbeddings(
    api_key=qwen_api_key,
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    model="text-embedding-v3"
)

# Create vector store directly using the embedding model
vector_store = FAISS.from_texts(
    [doc.page_content for doc in texts], 
    qwen_embeddings,
    metadatas=[doc.metadata for doc in texts]
)

# Initialize our custom DeepSeek LLM
llm = DeepSeekLLM(
    api_key=deepseek_api_key,
    api_base=DEEPSEEK_API_BASE,
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
    result = qa_chain.invoke({"query": query})
    return result["result"]

if __name__ == "__main__":
    query = "Wat is het annuleringsbeleid?"
    response = get_response(query)
    print(response)

app = Flask(__name__)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    query = data.get("query", "")
    response = get_response(query)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)