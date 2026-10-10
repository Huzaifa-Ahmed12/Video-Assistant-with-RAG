import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough,RunnableLambda
from core.vector_store import load_vector_store, build_vector_store, get_retriever

def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-3.8-flash",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])

def build_rag_chain(transcript:str):
    vector_store=build_vector_store(transcript)
    retriever=get_retriever(vector_store,k=5)
    llm=get_llm()
    prompt=ChatPromptTemplate.from_messages([
        ("system","""You are an expert meeting assistant. Answer the user's question based only from the meeting transcript context provided below.
        If answer is not in context just simple answer. I could not find this information in the meeting.
        Context is {context}"""),
        ("human","{question}")
    ])

    rag_chain=(
        {"context":retriever | RunnableLambda(format_docs),
         "question":RunnablePassthrough()
         }
        |prompt
        |llm
        |StrOutputParser()
    )
    return rag_chain

def load_rag_chain():
    vector_store=load_vector_store()
    retriever=get_retriever(vector_store,k=5)
    llm=get_llm()
    prompt=ChatPromptTemplate.from_messages([
        ("system","""You are an expert meeting assistant. Your job is to answer the user's question only from the meeting transcript context provided below.
        If answer is not in meeting context simple answer. I could not find this information in the meeting.
        The context is {context}"""),
        ("human","{question}")       
    ])
    rag_chain=(
        {"context":retriever | RunnableLambda(format_docs),
        "question":RunnablePassthrough()
        }
        |prompt
        |llm
        |StrOutputParser()
    )
    return rag_chain

def ask_question(rag_chain,question:str)->str:
    print(f"Question: {question}")
    answer=rag_chain.invoke(question)
    print(f"Answer: {answer}")
    return answer