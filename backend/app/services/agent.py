from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from app.core.vector_store import get_collection
from app.core.config import settings
from app.schemas.profile import UserProfile
from typing import List
import json

# ── Tool 1: Retrieve grounded policy chunks from Chroma ──────────────────────
@tool
def retrieve_policy_chunks(query: str) -> str:
    """
    Retrieve the most relevant policy document chunks from the vector store.
    ALWAYS call this tool before making any claim about a policy's coverage,
    exclusions, premiums, waiting periods, or benefits.
    Never rely on training knowledge for policy facts.
    Args:
        query: A natural language query describing what policy information is needed.
    Returns:
        Concatenated relevant chunks with source attribution.
    """
    collection = get_collection()
    results = collection.query(query_texts=[query], n_results=6)
    if not results or not results["documents"][0]:
        return "No relevant policy information found in the uploaded documents."
    
    output_parts = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        source = f"[Source: {meta.get('policy_name', 'Unknown')} by {meta.get('insurer', 'Unknown')}]"
        output_parts.append(f"{source}\n{doc}")
    return "\n\n---\n\n".join(output_parts)

# ── Tool 2: Get all policy names available in the vector store ────────────────
@tool
def list_available_policies() -> str:
    """
    Returns a list of all policy documents currently in the knowledge base.
    Call this first to know what policies are available before retrieving chunks.
    """
    collection = get_collection()
    results = collection.get()
    if not results or not results["metadatas"]:
        return "No policies uploaded yet."
    seen = set()
    policies = []
    for meta in results["metadatas"]:
        key = f"{meta.get('policy_name')} by {meta.get('insurer')}"
        if key not in seen:
            seen.add(key)
            policies.append(key)
    return json.dumps(policies)

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are Aarogya, an empathetic AI insurance advisor at AarogyaAid.
Your sole purpose is to help patients navigate health insurance with warmth, clarity, and honesty.

CORE RULES — follow every one of these without exception:
1. GROUNDING: You MUST call retrieve_policy_chunks before stating any fact about a policy.
   Never use your training knowledge for coverage details, premiums, exclusions, or waiting periods.
   If information is not in the uploaded documents, say so explicitly.
2. EMPATHY FIRST: Before presenting any numbers or policy names, acknowledge the user's health
   situation with warmth. A user disclosing diabetes or cardiac conditions may be doing so for
   the first time in a digital context — treat that with care.
3. DEFINE ALL JARGON: The first time you use a term (waiting period, co-pay, sub-limit,
   deductible, exclusion, cashless claim), define it in plain English inline.
4. SCOPE GUARDRAIL: If a user asks for medical advice (e.g., "should I get this surgery?",
   "is my medication safe?"), respond warmly but firmly: you can only advise on insurance
   coverage, not medical decisions. Recommend they consult their doctor.
5. NO DEAD ENDS: If the best available policy still has limitations for the user's profile,
   always offer an alternative path or next step. Never leave the user with a closed door.
6. SESSION MEMORY: You already have the user's profile. Never re-ask for age, conditions,
   income, or city. Use what you know to personalise every response.

RECOMMENDATION OUTPUT FORMAT:
When producing the initial recommendation, structure your response as valid JSON with these exact keys:
{
  "peer_comparison": [
    {"policy_name": "", "insurer": "", "premium_per_year": "", "cover_amount": "",
     "waiting_period": "", "key_benefit": "", "suitability_score": ""}
  ],
  "coverage_detail": {
    "inclusions": "", "exclusions": "", "sub_limits": "", "copay_percent": "", "claim_type": ""
  },
  "why_this_policy": "",
  "recommended_policy_name": "",
  "source_documents": []
}

The peer_comparison must include at least 2-3 policies.
The why_this_policy must be 150-250 words and reference at least 3 of the 6 profile fields by name.
All data must come from retrieved document chunks, not training knowledge.
"""

def build_profile_context(profile: UserProfile) -> str:
    conditions = ", ".join(profile.pre_existing_conditions)
    return f"""USER PROFILE (do not re-ask for any of this information):
- Name: {profile.full_name}
- Age: {profile.age} years
- Lifestyle: {profile.lifestyle}
- Pre-existing conditions: {conditions}
- Annual income band: {profile.income_band}
- City tier: {profile.city_tier}"""

def create_agent():
    llm = ChatOpenAI(model=settings.LLM_MODEL, api_key=settings.OPENAI_API_KEY, temperature=0.1)
    tools = [retrieve_policy_chunks, list_available_policies]
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_openai_tools_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=6)

def get_recommendation(profile: UserProfile) -> dict:
    """Run the agent to produce a structured recommendation from RAG-grounded data."""
    agent_executor = create_agent()
    profile_ctx = build_profile_context(profile)
    query = f"""{profile_ctx}

Please provide a full insurance recommendation for this user.
First call list_available_policies, then call retrieve_policy_chunks with relevant queries
(e.g., query for the user's conditions, income band, and city tier).
Return your response as the JSON structure defined in your instructions."""
    
    result = agent_executor.invoke({"input": query})
    output = result["output"]
    
    # Extract JSON from agent output
    import re
    json_match = re.search(r'\{.*\}', output, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    raise ValueError(f"Agent did not return valid JSON. Output: {output}")

def chat_with_agent(profile: UserProfile, recommended_policy: str, history: list, message: str) -> dict:
    """Handle a follow-up chat turn with full session context."""
    agent_executor = create_agent()
    profile_ctx = build_profile_context(profile)
    
    chat_history = []
    for turn in history:
        if turn["role"] == "user":
            chat_history.append(HumanMessage(content=turn["content"]))
        else:
            chat_history.append(AIMessage(content=turn["content"]))
    
    query = f"""{profile_ctx}
Currently recommended policy: {recommended_policy}

User question: {message}

Remember: call retrieve_policy_chunks if you need policy-specific facts.
If the user asks about a term, define it in plain English and give a realistic example using their actual profile."""
    
    result = agent_executor.invoke({"input": query, "chat_history": chat_history})
    return {"reply": result["output"], "sources": []}
