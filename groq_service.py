import os
import logging
from flask import session
from groq import Groq

# Set up logging
logging.basicConfig(level=logging.INFO)

# Get Groq API Key from environment
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# Model to use
GROQ_MODEL = "llama-3.3-70b-versatile"

# The system prompt defines the assistant's behavior
SYSTEM_PROMPT = """
You are an intelligent research assistant specialized in helping with research papers, patents, 
and academic workflows. Your responsibilities include:
1. Research Paper Management: Help users track, find, and organize research papers.
2. Literature Search & Citation Management: Assist with finding relevant papers and generating citations.
3. Research Notes & Summarization: Summarize papers and help organize research notes.
4. Patent Search & Analysis: Find and analyze patents related to specific technologies.
5. Patent Filing & Best Practices: Provide guidance on patent filing procedures.
6. Research Workflow & Productivity: Help users manage their research workflow.
7. Collaboration & Exporting: Assist with sharing research information.
8. AI Insights & Trends: Identify emerging research trends.
9. Research Ethics & Compliance: Provide guidance on ethical research practices.

If asked about topics outside research, journals, or patents, politely redirect the conversation 
to relevant research topics.
Format your responses with clear headings and concise information. Use bullet points when appropriate 
for readability. Provide citations when referencing specific information.
"""

# Dictionary of helpful responses for different categories of queries (Fallback mode)
FALLBACK_RESPONSES = {
    "general": "I'm here to help with your research assistant needs. How can I help you today?",
    "paper_search": "To search for papers, use the Papers section. You can manually enter details or search via keyword through our integration with research databases.",
    "citation": "You can generate citations for papers by visiting the Papers section, selecting a paper, and using the citation generator.",
    "patent": "To find patents, use the Patents section. You can search by title, number, or inventor through the search interface.",
    "note": "The Notes section allows you to create, organize, and link notes to your papers and patents.",
    "summarize": "You can create your own summaries in the Notes section and link them to specific papers or patents for better organization.",
    "help": "This Research Assistant helps you manage papers, patents, and research notes. Navigate using the menu to explore all features."
}

def generate_fallback_response(user_message):
    user_msg = user_message.lower()
    if "search" in user_msg and ("paper" in user_msg or "article" in user_msg or "journal" in user_msg):
        return FALLBACK_RESPONSES["paper_search"]
    elif "citation" in user_msg or "cite" in user_msg or "reference" in user_msg:
        return FALLBACK_RESPONSES["citation"]
    elif "patent" in user_msg:
        return FALLBACK_RESPONSES["patent"]
    elif "note" in user_msg or "write" in user_msg or "record" in user_msg:
        return FALLBACK_RESPONSES["note"]
    elif "summarize" in user_msg or "summary" in user_msg:
        return FALLBACK_RESPONSES["summarize"]
    elif "help" in user_msg or "guide" in user_msg or "how" in user_msg:
        return FALLBACK_RESPONSES["help"]
    else:
        return FALLBACK_RESPONSES["general"]

def get_chat_history(user_id):
    """Retrieve chat history for the current user safely"""
    try:
        session_key = f'chat_history_{user_id}'
        if session_key not in session:
            session[session_key] = []
        return session[session_key]
    except Exception:
        return []

def set_chat_history(user_id, history):
    """Save chat history for the current user safely"""
    try:
        session_key = f'chat_history_{user_id}'
        session[session_key] = history
    except Exception:
        pass

def get_groq_response(user_message, user_id, context=""):
    """
    Get response from Groq API using the official Python SDK.
    Uses llama-3.3-70b-versatile model for fast, high-quality responses.
    """
    logging.info(f"Generating Groq response for user {user_id}")

    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        logging.warning("No Groq API key found. Using fallback.")
        return generate_fallback_response(user_message)

    # Get chat history for context
    chat_history = get_chat_history(user_id)

    # Build messages list with system prompt, history, and current message
    updated_system_prompt = SYSTEM_PROMPT
    if context:
        updated_system_prompt += f"\n\nUse the following retrieved context to help answer the user's question:\n{context}"
        
    messages = [{"role": "system", "content": updated_system_prompt}]

    # Add recent chat history for context (last 10 exchanges)
    for entry in chat_history[-10:]:
        role = entry.get("role", "user")
        if role in ("user", "assistant"):
            messages.append({"role": role, "content": entry["content"]})

    # Add the current user message
    messages.append({"role": "user", "content": user_message})

    try:
        client = Groq(api_key=GROQ_API_KEY)

        chat_completion = client.chat.completions.create(
            messages=messages,
            model=GROQ_MODEL,
            temperature=0.7,
            max_tokens=1024,
            top_p=0.95,
        )

        text_response = chat_completion.choices[0].message.content

        # Update history
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": text_response})
        if len(chat_history) > 20:
            chat_history = chat_history[-20:]
        set_chat_history(user_id, chat_history)

        return text_response

    except Exception as e:
        logging.error(f"Exception during Groq API call: {str(e)}")
        return generate_fallback_response(user_message)
