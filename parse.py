from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatMessagePromptTemplate

model = OllamaLLM(model="llama3.2")

<<<<<<< HEAD
def parse_content(content_chunks, query):
=======
def parse_ollama(content_chunks, query):
>>>>>>> e76133e (Attached Ollama LLM Model)
    prompt = ChatMessagePromptTemplate.from_template(
        "You are a helpful assistant that extracts and analyse relevant information from the provided content based on the user's query.\n"
        "Content: {content_chunks}\n"
        "User Query: {query}\n"
        "Please provide a concise and relevant response."
    )

    result=[]
    for i, chuck in enumerate(content_chunks):
        response = model.predict_messages(
            prompt.format_messages(content=chuck, query=query)
        )
        result.append(response.content)


    return result