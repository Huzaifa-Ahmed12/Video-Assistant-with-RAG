from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
import os

def get_llm():
    return ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite",gemini_api_key=os.getenv("GEMINI_API_KEY"),temperature=0.2)

def build_chain(system_prompt:str):
    llm=get_llm()
    prompt=ChatPromptTemplate.from_messages([
        ("system",system_prompt),
        ("human","{text}"),
    ])

    return (
        RunnablePassthrough() | RunnableLambda(lambda x:{"text":x}) | prompt | llm | StrOutputParser()
    )

def extract_action_items(transcript:str)->str:
    chain=build_chain(
        """Your are an expert meeting analyst. From the meeting transcript extract all the actionable items:
        Extract 
        1. Task Description \n
        2. Owner (who is repsonsible)
        3. Deadline for the task if mentioned
        Format these into a number list and if none found say No Action Items Found"""
    )
    return (chain.invoke(transcript))

def extract_key_decision(transcript:str)->str:
    chain=build_chain(
        """You are an expert meeting analyst. From the meeting transcript extract all key decisions made in number list.
        And if none found then say No Key Decisions Found"""
    )
    return (chain.invoke(transcript))

def extract_questions(transcript:str)->str:
    chain=build_chain(
        """You are an expert meeting analyst. From the meeting Transcript extract all the unresolved questions or topic needing follow up.
        Format those in the form of numbered List and if none found say No Questions Found"""
    )
    return(chain.invoke(transcript))