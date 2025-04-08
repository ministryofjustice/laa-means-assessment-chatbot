# This is the first draft of the LLM which will power the AI model.
# It is able to read the PDF of the lord chancellors guidance and answer basic questions about it.
from langchain import hub
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.llms import GPT4All
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

# Load PDF file
loader  = PyMuPDFLoader(file_path= os.path.join("../data", "LCGuidance.pdf"))
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_splits = text_splitter.split_documents(docs)

# Create embeddings and vector store
embeddings = GPT4AllEmbeddings()
vector_store = InMemoryVectorStore(embeddings)
_ = vector_store.add_documents(documents=all_splits)

# Create model and prompt
model = GPT4All(model="Meta-Llama-3-8B-Instruct.Q4_0.gguf")
prompt = hub.pull("rlm/rag-prompt")

qa_chain = RetrievalQA.from_chain_type(
    llm= GPT4All(model="Meta-Llama-3-8B-Instruct.Q4_0.gguf"),
    chain_type="stuff",
    retriever=vector_store.as_retriever()
)

# Query the PDF
question = input("> ")
response = qa_chain.invoke({"query": question})
print(response['result'])