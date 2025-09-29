from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma


# 🔹 Step 1: Initialize LLM + embeddings
llm = OllamaLLM(model="llama3.2")  
embeddings = OllamaEmbeddings(model="nomic-embed-text")  # fast + good quality

# 🔹 Step 2: Preprocess & store chunks in vector DB
def build_vector_db(content_chunks, persist_directory="chroma_db"):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.create_documents(content_chunks)
    db = Chroma.from_documents(docs, embeddings, persist_directory=persist_directory)
    return db

# 🔹 Step 3: Query function (retrieval + LLM)
def parse_ollama(content_chunks, query, persist_directory="chroma_db"):
    # Build / load DB
    db = build_vector_db(content_chunks, persist_directory=persist_directory)

    # Retrieve top-k relevant chunks
    retrieved_docs = db.similarity_search(query, k=3)
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    # Prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that extracts and analyses relevant information from the provided content based on the user's query."),
        ("human", "Context: {context}\nUser Query: {query}\nPlease provide a concise and relevant response.")
    ])

    messages = prompt.format_messages(context=context, query=query)
    response = llm.invoke(messages)

    return response
