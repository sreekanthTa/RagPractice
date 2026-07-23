from langchain_groq import ChatGroq
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from pathlib import Path


llm=ChatGroq(
   api_key="api_key",
   model="llama-3.3-70b-versatile"
)
response = llm.invoke("Hello!")
print(response.content)




def get_pdf_pages (path):
    Pages = []

    doc_pages = PdfReader(path)
    for page in doc_pages.pages:
        Pages.append(page.extract_text())

    return Pages


def chunk_pdf(Pages, chunk_size=300, overlap=50):
  
  Chunks = []

  splitter = RecursiveCharacterTextSplitter(
     chunk_size= chunk_size,
     chunk_overlap = overlap,

  )

  for page in Pages:
      texts = splitter.split_text(page)
      Chunks.extend(texts)

  return Chunks



embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)




def create_chorma_db(chunks):
    client = chromadb.PersistentClient(path="./chroma_db")

    collection = client.create_collection(name="RAG_Collection")
    
    vectorstore = Chroma.from_documents(
        documents = chunks,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )

    return vectorstore

DB_DIR = "./chroma_db"

if Path(DB_DIR).exists():
    print("Loading existing ChromaDB...")

    vectorstore = Chroma(
        persist_directory=DB_DIR,
        embedding_function=embeddings
    )

    query = "What is  a Rag ?"

    results = vectorstore.similarity_search(
        query,
        k=2
    )

    for doc in results:
        print(doc.page_content)
        print(doc.metadata)

else:

    GetPDF
    pdf = get_pdf_pages(r"C:\Users\sreek\RagPractice\data\sample_rag_chromadb.pdf",)
    print("+++++++++++PDF PAGES+++++++++++++")
    print(pdf[0])

    print("+++++++++++++PDF Chunks++++++++++=")
    chunks = chunk_pdf(pdf)
    print(chunks[0])

    print("+++++++++++EMBEDDING++++++++++++")
    create_chorma_db(chunks)




