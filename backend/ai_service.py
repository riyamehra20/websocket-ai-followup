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
                  'can', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'me',
                  'you', 'he', 'she', 'we', 'they', 'them', 'him'}
    
    words = re.findall(r'\b\w+\b', text.lower())
    key_words = [w for w in words if w not in stop_words and len(w) > 2]
    
    return key_words if key_words else ['that']

async def generate_followup_question(user_input, history, followup_number):
    """Generate AI follow-up question using history to avoid repetition"""
    
    # Extract key words from the LATEST user input
    words = extract_key_words(user_input)
    
    # Build conversation history for context
    history_text = ""
    previous_questions = []
    
    for msg in history:
        if msg["role"] == "user":
            history_text += f"User said: {msg['content']}\n"
        else:
            history_text += f"AI asked: {msg['content']}\n"
            previous_questions.append(msg['content'])
    
    # Create explicit instructions to avoid repetition
    avoid_text = ""
    if previous_questions:
        avoid_text = f"\nPrevious questions you already asked:\n" + "\n".join([f"- {q}" for q in previous_questions])
        avoid_text += f"\n\nDO NOT repeat or rephrase these questions. Ask something completely NEW and DIFFERENT."
    
    # Build the prompt
    prompt = f"""You are conducting a conversational interview. Generate follow-up question #{followup_number} of 3.

Conversation history:
{history_text}

User's latest response: "{user_input}"

Key words from user's response: {', '.join(words[:3])}

{avoid_text}

STRICT REQUIREMENTS:
1. Your question MUST include at least ONE word from this list: {', '.join(words[:3])}
2. DO NOT ask about something you already asked
3. Make it natural, conversational, and under 20 words
4. Focus on a DIFFERENT aspect than previous questions
5. Return ONLY the question text, no explanations or formatting

Generate the question now:"""
    
    try:
        response = model.generate_content(prompt)
        question = response.text.strip()
        
        # Clean up the response
        question = question.replace('*', '').replace('#', '').strip()
        
        # Remove any quotes if Gemini added them
        question = question.strip('"').strip("'")
        
        # Ensure it ends with a question mark
        if not question.endswith('?'):
            question += '?'
        
        return question
        
    except Exception as e:
        print(f"AI Error: {e}")
        # Fallback question using a word from the input
        fallback_word = words[0] if words else "that"
        fallback_questions = [
            f"Can you elaborate more on {fallback_word}?",
            f"What makes {fallback_word} significant to you?",
            f"How does {fallback_word} affect your daily life?"
        ]
        return fallback_questions[followup_number - 1] if followup_number <= 3 else fallback_questions[0]