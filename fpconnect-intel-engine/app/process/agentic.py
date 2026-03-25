"""
Agentic Intelligence Workflows:
1. Research Agent: Crawls external context if needed.
2. Triage Agent: Classifies severity and topic autonomously.
3. RCA Agent: Generates root-cause analysis based on context + Memory (RAG).
"""

from typing import Dict, Any, List
import os
import requests
import json

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain.prompts import ChatPromptTemplate
    from langchain_core.documents import Document
except Exception:
    ChatOpenAI = None
    OpenAIEmbeddings = None
    FAISS = None
    ChatPromptTemplate = None
    Document = None

# In-memory vector store for demo (Semantic Memory / RAG Platform)
_vector_store = None

def get_vector_store():
    global _vector_store
    if _vector_store is None:
        key = os.getenv("OPENAI_API_KEY")
        if not key or not OpenAIEmbeddings or not FAISS or not Document:
            return None
        embeddings = OpenAIEmbeddings(openai_api_key=key)
        # Dummy init to avoid crashes on first search
        _vector_store = FAISS.from_documents([Document(page_content="Baseline knowledge initialized", metadata={"type": "init"})], embeddings)
    return _vector_store

def add_memory(text: str, meta: dict):
    store = get_vector_store()
    if store and Document:
        store.add_documents([Document(page_content=text, metadata=meta)])

def search_memory(query: str, k: int = 2) -> str:
    store = get_vector_store()
    if not store:
        return "Semantic memory unavailable (No OpenAI API Key)."
    docs = store.similarity_search(query, k=k)
    return "\n\n".join([d.page_content for d in docs])

def research_agent(url: str, text: str) -> str:
    """Agent 1: Research - Fetches additional context if the text is too short."""
    text_safe = (text or "")
    if len(text_safe.split()) > 300:
        return text_safe # Already enough context
        
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            if BeautifulSoup:
                soup = BeautifulSoup(r.text, 'html.parser')
                paragraphs = soup.find_all('p')
                enriched_text = " ".join([p.get_text() for p in paragraphs])
                return text_safe + "\n\n[Enriched by Research Agent]:\n" + enriched_text[:2000]
    except Exception:
        pass
    return text_safe

def triage_agent(text: str) -> Dict[str, Any]:
    """Agent 2: Triage - Classifies topic, severity, and recommends assignment autonomously."""
    key = os.getenv("OPENAI_API_KEY")
    if not key or not ChatOpenAI or not ChatPromptTemplate:
        return {"severity": "Low", "topic": "General", "summary": text[:100]}
    
    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini", openai_api_key=key)
    prompt = ChatPromptTemplate.from_template(
        "You are an expert Triage Agent. Analyze this text and output JSON with exact keys: "
        "'topic' (string), 'severity' (High, Medium, or Low), 'summary' (concise description), and 'recommended_action' (string).\n\n"
        "Respond ONLY with valid JSON.\n\nText: {text}"
    )
    chain = prompt | llm
    try:
        resp = chain.invoke({"text": text})
        content = resp.content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
        return json.loads(content.strip())
    except Exception as e:
        return {"severity": "Medium", "topic": "General", "summary": "Failed to triage.", "error": str(e)}

def rca_agent(text: str, triage_data: dict) -> str:
    """Agent 3: Root Cause Analysis - Proposes solutions using Semantic Memory."""
    key = os.getenv("OPENAI_API_KEY")
    if not key or not ChatOpenAI or not ChatPromptTemplate:
        return "RCA unavailable."
    
    memory_context = search_memory(text)
    
    llm = ChatOpenAI(temperature=0.2, model="gpt-4o-mini", openai_api_key=key)
    prompt = ChatPromptTemplate.from_template(
        "You are an RCA Agent (Root Cause Analysis). Based on the new issue and past resolved issues below (Semantic Memory), "
        "provide a Root Cause Hypothesis and an Action Plan.\n\n"
        "### Memory Context (Past Issues):\n{memory}\n\n"
        "### New Issue:\n{text}\n\n"
        "### Triage Data:\n{triage}\n\n"
        "Output a markdown Action Plan with a proposed root-cause and step-by-step resolution."
    )
    chain = prompt | llm
    resp = chain.invoke({"text": text, "memory": memory_context, "triage": json.dumps(triage_data)})
    
    # Store this interaction in memory so future agents can learn from it
    add_memory(
        f"Issue: {triage_data.get('summary', 'Unknown')} | RCA: {resp.content[:500]}", 
        {"source": "agent_learning", "topic": triage_data.get('topic', 'General')}
    )
    
    return resp.content


def run_agentic_workflow(url: str, content_text: str) -> Dict[str, Any]:
    """The master orchestrator of the agent workflow."""
    # Step 1: Research
    enriched = research_agent(url, content_text)
    
    # Step 2: Triage
    triage = triage_agent(enriched)
    
    # Step 3: RCA & Memory Update
    rca = rca_agent(enriched, triage)
    
    return {
        "enriched_text": enriched,
        "triage": triage,
        "rca": rca
    }
