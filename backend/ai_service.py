import google.generativeai as genai
import os
from dotenv import load_dotenv
import re

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

def extract_key_words(text):
    """Extract meaningful words from user input"""
    stop_words = {'i', 'a', 'the', 'is', 'are', 'was', 'were', 'it', 'this', 'that', 
                  'am', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 
                  'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must',
                  'can', 'my', 'your', 'his', 'her', 'its', 'our', 'their'}
    
    words = re.findall(r'\b\w+\b', text.lower())
    key_words = [w for w in words if w not in stop_words and len(w) > 2]
    
    return key_words[:3] if key_words else ['that']

async def generate_followup_question(user_input, history, followup_number):
    """Generate AI follow-up question using history to avoid repetition"""
    
    # 1. Format the history so Gemini knows what was already said
    history_context = ""
    for msg in history:
        role = "User" if msg["role"] == "user" else "AI"
        history_context += f"{role}: {msg['content']}\n"

    # 2. Extract key words from the LATEST input
    words = extract_key_words(user_input)
    
    # 3. Create a smart prompt
    prompt = f"""
    Conversation so far:
    {history_context}
    
    The user just said: "{user_input}"
    
    Task: Generate Follow-up Question #{followup_number}.
    Instructions:
    - Do NOT repeat the question "Can you tell me more about 'hate'?" or any previous questions.
    - Use a new word from this list if possible: {', '.join(words)}.
    - Keep it short, conversational, and under 15 words.
    - Generate ONLY the question text.
    """
    
    try:
        response = model.generate_content(prompt)
        question = response.text.strip()
        return question.replace('*', '').replace('#', '').strip()
    except Exception as e:
        print(f"AI Error: {e}")
        return f"How do you feel about {words[0]} specifically?"