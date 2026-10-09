from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
import os

def get_llm():
    return ChatGoogleGenerativeAI(model="gemini-3.8-flash",google_api_key=os.getenv("GEMINI_API_KEY"))

def build_chain(system_prompt:str):
    llm=get_llm()
    prompt=ChatPromptTemplate.from_messages([
        ("system",system_prompt),
        ("human","{text}"),
    ])

    return (
        RunnablePassthrough() | RunnableLambda(lambda x:{"text":x}) | prompt | llm | StrOutputParser()
    )

def split_transcript(transcript:str)->list:
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=200
    )
    return splitter.split_text(transcript)

def extract_action_items(transcript:str)->str:

    chain=build_chain(
        """You are an expert meeting analyst. From the meeting transcript extract all the actionable items:
        Extract 
        1. Task Description 
        2. Owner (who is repsonsible)
        3. Deadline for the task if mentioned
        Format these into a number list and if none found say No Action Items Found"""
    )
    if len(transcript) <= 40_000:
        return chain.invoke(transcript)
    
    chunks=split_transcript(transcript)
    chunk_invoke=[chain.invoke(chunk) for chunk in chunks]
    combined="\n\n" .join(chunk_invoke)
    merge_chain = build_chain(
        """You are an expert meeting analyst. Below are action items extracted from different
        parts of the same meeting. Merge them into one final numbered list.
        - Remove duplicates (parts overlap, so the same task may appear twice).
        - Ignore any 'No Action Items Found' lines.
        - Keep the owner and deadline for each task.
        If nothing remains, say No Action Items Found."""
    )
    return (merge_chain.invoke(combined))

def extract_key_decision(transcript:str)->str:
    chain=build_chain(
        """You are an expert meeting analyst. From the meeting transcript extract all key decisions made in number list.
        And if none found then say No Key Decisions Found"""
    )
    if len(transcript)<=40_000:
        return chain.invoke(transcript)
    chunks=split_transcript(transcript)
    chunk_invoke=[chain.invoke(chunk) for chunk in chunks]
    combined="\n\n" .join(chunk_invoke)
    merge_chain = build_chain(
    """You are an expert meeting analyst. Below are key decisions extracted from different
    parts of the same meeting. Merge them into one final numbered list.
    - Remove duplicates (parts overlap, so the same decision may appear twice).
    - Ignore any 'No Key Decisions Found' lines.
    - Keep each decision clear and specific.
    If nothing remains, say No Key Decisions Found."""
    )
    return (merge_chain.invoke(combined))

def extract_questions(transcript:str)->str:
    chain=build_chain(
        """You are an expert meeting analyst. From the meeting Transcript extract all the unresolved questions or topic needing follow up.
        Format those in the form of numbered List and if none found say No Questions Found"""
    )
    if len(transcript) <=40_000:
        return(chain.invoke(transcript))
    chunks=split_transcript(transcript)
    chunk_invoke=[chain.invoke(chunk) for chunk in chunks]
    combined="\n\n".join(chunk_invoke)
    merge_chain=build_chain(
          """You are an expert meeting analyst. Below are unresolved questions and follow-up topics
    extracted from different parts of the same meeting. Merge them into one final numbered list.
    - Remove duplicates (parts overlap, so the same question may appear twice).
    - Ignore any 'No Questions Found' lines.
    - Remove any question that was clearly answered later in another part.
    If nothing remains, say No Questions Found."""
    )
    return (merge_chain.invoke(combined))