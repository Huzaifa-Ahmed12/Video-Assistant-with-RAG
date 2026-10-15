from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
import os

def get_llm():
    return ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite",google_api_key=os.getenv("GEMINI_API_KEY"))

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
        """You are analyzing a meeting transcript. Extract every action item: a task that a person committed to or was assigned.

Rules:
- Use only what is said in the transcript. Never invent tasks, owners or deadlines.
- The transcript has no speaker labels. Name an owner only if the transcript makes it clear who it is (for example, someone is addressed by name or introduces themselves). Otherwise write "Not specified".
- Write a deadline only if one is mentioned. Otherwise write "Not specified".

Write each action item in exactly this format:
1. Task Description: <the task>
   Owner: <person or "Not specified">
   Deadline: <date or time or "Not specified">

Output only the list, with no introduction and no closing remarks.
If there are no action items, output exactly: None
"""
    )
    if len(transcript) <= 40_000:
        return chain.invoke(transcript)
    
    chunks=split_transcript(transcript)
    chunk_invoke=[chain.invoke(chunk) for chunk in chunks]
    combined="\n\n" .join(chunk_invoke)
    merge_chain = build_chain(
        """Below are action items extracted from different parts of the same meeting. Merge them into one final numbered list.
- Remove duplicates (the parts overlap, so the same task may appear twice).
- Keep the Task Description / Owner / Deadline format for every item and number from 1.
- Output only the list, with no introduction.
If nothing remains, output exactly: None
"""
    )
    return (merge_chain.invoke(combined))

def extract_key_decision(transcript:str)->str:
    chain=build_chain(
       """You are analyzing a meeting transcript. Extract the key decisions the group made: choices, approvals, or agreed changes of plan.

Rules:
- Use only what is said in the transcript. Never invent decisions.
- Do NOT include tasks assigned to individuals. Those are action items, not decisions.
- A topic that was only discussed or left open is not a decision.

Output a numbered list with one decision per line, with no bold text, no introduction and no closing remarks.
If there are no decisions, output exactly: None
"""
    )
    if len(transcript)<=40_000:
        return chain.invoke(transcript)
    chunks=split_transcript(transcript)
    chunk_invoke=[chain.invoke(chunk) for chunk in chunks]
    combined="\n\n" .join(chunk_invoke)
    merge_chain = build_chain(
   """Below are key decisions extracted from different parts of the same meeting. Merge them into one final numbered list.
- Remove duplicates (the parts overlap, so the same decision may appear twice).
- Keep each decision clear and specific.
- Output only the list, with no introduction.
If nothing remains, output exactly: None
"""
    )
    return (merge_chain.invoke(combined))

def extract_questions(transcript:str)->str:
    chain=build_chain(
        """You are analyzing a meeting transcript. Extract the questions that were raised but left unanswered, and any topics that need follow-up.

Rules:
- Use only what is said in the transcript.
- Skip questions that were answered later in the meeting.
- Skip rhetorical questions and small talk.

Output a numbered list with one item per line, with no bold text, no introduction and no closing remarks.
If there are none, output exactly: None
"""
    )
    if len(transcript) <=40_000:
        return(chain.invoke(transcript))
    chunks=split_transcript(transcript)
    chunk_invoke=[chain.invoke(chunk) for chunk in chunks]
    combined="\n\n".join(chunk_invoke)
    merge_chain=build_chain(
         """Below are unresolved questions and follow-up topics extracted from different parts of the same meeting. Merge them into one final numbered list.
- Remove duplicates (the parts overlap, so the same question may appear twice).
- Remove any question that was clearly answered in another part.
- Output only the list, with no introduction.
If nothing remains, output exactly: None
"""

    )
    return (merge_chain.invoke(combined))