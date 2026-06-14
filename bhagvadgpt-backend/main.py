from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from typing import List, Dict, Any
import json
from fastapi.responses import StreamingResponse
from groq import RateLimitError, InternalServerError
import random
import time

load_dotenv() # This loads the hidden key from the .env file safely

app = FastAPI(title="BhagvadGPT API")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

print("Initializing BhagvadGPT Backend...")

# API Key Rotation Setup - Keys from DIFFERENT accounts for true 5x capacity
GROQ_API_KEYS = [
    os.getenv("GROQ_API_KEY1"),
    os.getenv("GROQ_API_KEY2"), 
    os.getenv("GROQ_API_KEY3"),
    os.getenv("GROQ_API_KEY4"),
    os.getenv("GROQ_API_KEY5"), 
]

# Filter out None values in case .env key is missing
GROQ_API_KEYS = [key for key in GROQ_API_KEYS if key]

# Track key usage and failures
key_stats = {key: {"uses": 0, "failures": 0, "last_failure": 0} for key in GROQ_API_KEYS}
current_key_index = 0

def get_next_api_key():
    """Get the next API key in rotation, skipping recently failed keys"""
    global current_key_index
    
    current_time = time.time()
    available_keys = []
    
    # Find keys that haven't failed recently (within last 60 seconds)
    for i, key in enumerate(GROQ_API_KEYS):
        if current_time - key_stats[key]["last_failure"] > 60:
            available_keys.append(i)
    
    # If all keys failed recently, use any key (they might have recovered)
    if not available_keys:
        available_keys = list(range(len(GROQ_API_KEYS)))
    
    # Round-robin through available keys
    current_key_index = (current_key_index + 1) % len(GROQ_API_KEYS)
    while current_key_index not in available_keys:
        current_key_index = (current_key_index + 1) % len(GROQ_API_KEYS)
    
    selected_key = GROQ_API_KEYS[current_key_index]
    key_stats[selected_key]["uses"] += 1
    
    print(f"🔑 Using API key #{current_key_index + 1} (Used {key_stats[selected_key]['uses']} times)")
    return selected_key

def mark_key_failed(api_key):
    """Mark a key as failed so it's temporarily skipped"""
    key_stats[api_key]["failures"] += 1
    key_stats[api_key]["last_failure"] = time.time()
    print(f"⚠️ API key marked as failed (Total failures: {key_stats[api_key]['failures']})")

def create_llm_with_key(api_key):
    """Create a new LLM instance with the specified API key"""
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.6,
        groq_api_key=api_key
    )

print(f"✅ Loaded {len(GROQ_API_KEYS)} Groq API keys for rotation")

# 1. Connect to our pure ChromaDB
try:
    client = chromadb.PersistentClient(path="./gita_knowledge_base")
    collection = client.get_collection(name="bhagavad_gita")
    print("✅ Connected to local Chroma vector database.")
except Exception as e:
    print(f"❌ Database Error: Ensure you ran build_db.py first! Error: {e}")

# 2. The Ultimate BhagvadGPT Production Prompt
prompt_template = PromptTemplate.from_template("""
You are the core retrieval engine of BhagvadGPT. 
**How this connects to your situation:**
[Write a warm, empathetic, and profound explanation speaking DIRECTLY to {username}. Do not use robotic phrases like "This verse highlights" or "In your situation, this means." Speak to them as a wise, comforting spiritual friend. Validate their specific emotional pain or dilemma first, then weave the timeless wisdom of the shloka into gentle, actionable advice for their modern life.]
STEP 1: IDENTIFY IF THIS IS A VALID QUESTION
First, determine if the User Question is actually a question seeking guidance or wisdom.

NON-QUESTIONS include:
- Simple greetings (hi, hello, namaste, hey, good morning, etc.)
- Statements without questions (I am happy, today is nice, etc.)
- Casual conversation attempts (how are you, what's up, etc.)
- Single words or incomplete thoughts

If the User Question is a NON-QUESTION, you MUST output EXACTLY and ONLY this message:
"Kindly ask your question whose answer you want from the gita"

STEP 2: SUICIDE & SELF-HARM OVERRIDE (HIGHEST PRIORITY)
If the User Question mentions suicide, ending life, self-harm, or suicidal thoughts, you MUST completely ignore the provided context. You must output EXACTLY and ONLY this message:

"Namaste {username}, your life has immense value and purpose.

If you're in crisis, please reach out immediately:
🇮🇳 India: AASRA - 9820466726 | iCall - 9152987821
🇺🇸 USA: 988 (Suicide & Crisis Lifeline)
🇬🇧 UK: 116 123 (Samaritans)

The Gita teaches that every life is sacred and has a divine purpose. Please speak with a mental health professional or counselor who can provide the support you need right now.

You are not alone. Help is available."

STEP 3: VIOLENCE & HARM OVERRIDE
If the User Question involves terrorism, murder, physical violence against others, or illegal acts, you MUST completely ignore the provided context. You must output EXACTLY and ONLY this message:
"Namaste, I am a spiritual guide meant to spread peace and dharma. I cannot and will not assist with violence, harm, or destructive actions. Please seek a path of the Gita."

STEP 4: OUT-OF-DOMAIN OVERRIDE
If the User Question is about mundane, modern, or non-spiritual topics (such as specific movies, TV shows, taking loans, banking, financial products, tech support, coding, etc.), you MUST NOT try to force a connection to the Gita. You must completely ignore the provided context and output EXACTLY and ONLY this message:
"Namaste! I am BhagvadGPT focused on the wisdom of the Bhagavad Gita. Kindly ask relavant questions only."

HOWEVER, if the question involves human emotions, relationships, workplace stress, mental health, or ethical dilemmas, even in a modern setting (e.g., "stress at work" or "family conflict"), you MUST treat these as valid spiritual inquiries and proceed to STEP 5.

STEP 5: IF THE QUESTION IS SAFE AND VALID, FORMAT YOUR RESPONSE
Your strictly enforced task is to output EXACTLY what is in the database, without summarizing, truncating, or altering the sacred text. 
You MUST format your response using EXACTLY the template below. Do not add any conversational filler before or after. Do not use generic bullet points.

Namaste! \nTo your situation these shlokas from the Gita are the best answers:

[FOR EACH VERSE IN THE CONTEXT, REPEAT THIS BLOCK EXACTLY:]
**[Reference]**
[Insert the ENTIRE Sanskrit shloka here EXACTLY as provided in the context. Do not cut a single word.]

**Translation:**
[Insert the EXACT English translation here.]

**How this connects to your situation:**
[Write a thoughtful, personalized explanation (3-5 sentences) that DIRECTLY addresses the user's specific question or problem. You must:
- Identify the core emotion, challenge, or dilemma in their question
- Explain how THIS specific verse provides wisdom for THEIR exact situation
- Use concrete language that bridges the ancient teaching to their modern context
- Make the connection feel natural and deeply relevant, not generic
- Base your explanation strictly on the 'Meaning & Purport' provided in the context, but apply it specifically to their case]
[END OF BLOCK]

Radhe Radhe!

Context Retrieved from Database:
{context}

User Question: {question}
""")

# Request Schema
class ChatRequest(BaseModel):
    message: str

from fastapi import Request, HTTPException

@app.post("/v1/chat/completions")
async def openai_adapter(request: Request):
    try:
        data = await request.json()
        user_message = data["messages"][-1]["content"]
        
        # Extract username if provided (LibreChat sends this in the 'user' field)
        username = data.get("user", "") if data.get("user") else "Friend"

        # 1. Search DB & Format Prompt
        results = collection.query(query_texts=[user_message], n_results=5)
        context_str = ""
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                doc = results['documents'][0][i]
                meta = results['metadatas'][0][i]
                context_str += f"\n[{meta['reference']}]\n{meta['shloka']}\nMeaning & Purport: {doc}\n"
        
        # 2. Get Answer from Groq with Rate Limit Protection and Key Rotation
        formatted_prompt = prompt_template.format(context=context_str, question=user_message, username=username)
        
        max_retries = len(GROQ_API_KEYS)  # Try all keys if needed
        final_content = None
        
        for attempt in range(max_retries):
            try:
                # Get next API key in rotation
                api_key = get_next_api_key()
                
                # Create LLM with this key
                llm = create_llm_with_key(api_key)
                
                # Try to get response
                response = llm.invoke(formatted_prompt)
                final_content = response.content
                print(f"✅ Successfully got response using key #{current_key_index + 1}")
                break  # Success! Exit retry loop
                
            except RateLimitError as e:
                print(f"⚠️ Rate limit hit on key #{current_key_index + 1}")
                mark_key_failed(api_key)
                
                if attempt < max_retries - 1:
                    print(f"🔄 Retrying with next API key... (Attempt {attempt + 2}/{max_retries})")
                    time.sleep(0.5)  # Small delay between retries
                    continue
                else:
                    print("❌ All API keys exhausted!")
                    final_content = "Namaste, BhagvadGPT is currently experiencing a high volume of requests. Please take a moment to meditate and try again shortly. 🙏\n\n(All API keys have reached their rate limits. They will reset automatically.)"
                    
            except Exception as e:
                error_msg = str(e)
                print(f"⚠️ API Error on key #{current_key_index + 1}: {error_msg}")
                
                # Check if it's an invalid API key error
                if "invalid_api_key" in error_msg.lower() or "401" in error_msg:
                    print(f"❌ Key #{current_key_index + 1} is INVALID - removing from rotation")
                    # Don't retry with invalid keys
                    mark_key_failed(api_key)
                    if attempt < max_retries - 1:
                        continue
                else:
                    mark_key_failed(api_key)
                    
                if attempt < max_retries - 1:
                    print(f"🔄 Retrying with next API key... (Attempt {attempt + 2}/{max_retries})")
                    time.sleep(0.5)  # Small delay between retries
                    continue
                else:
                    final_content = "A small disturbance has occurred in the ether. Please try again in a moment."

        # 3. Stream or JSON Response
        if data.get("stream"):
            async def stream_generator():
                # Chunk 1: Role
                chunk1 = {
                    "id": "chatcmpl-bhagvadgpt", "object": "chat.completion.chunk",
                    "model": data.get("model", "bhagvadgpt"),
                    "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}]
                }
                yield f"data: {json.dumps(chunk1)}\n\n"
                
                # Chunk 2: Content (The Answer or the Meditation Message)
                chunk2 = {
                    "id": "chatcmpl-bhagvadgpt", "object": "chat.completion.chunk",
                    "model": data.get("model", "bhagvadgpt"),
                    "choices": [{"index": 0, "delta": {"content": final_content}, "finish_reason": None}]
                }
                yield f"data: {json.dumps(chunk2)}\n\n"
                
                yield "data: [DONE]\n\n"
                
            return StreamingResponse(stream_generator(), media_type="text/event-stream")

        # Standard JSON fallback
        return {
            "id": "chatcmpl-bhagvadgpt", "object": "chat.completion",
            "model": data.get("model", "bhagvadgpt"),
            "choices": [{"index": 0, "message": {"role": "assistant", "content": final_content}, "finish_reason": "stop"}]
        }

    except Exception as e:
        print("🚨 CRITICAL BACKEND ERROR:", str(e))
        # Even on a total crash, we try to send a JSON error instead of just dying
        return {
            "choices": [{"message": {"role": "assistant", "content": "The connection to the Gita is weak. Please restart the backend."}}]
        }

@app.get("/api/key-stats")
async def get_key_stats():
    """Endpoint to check API key rotation statistics"""
    stats = []
    for i, key in enumerate(GROQ_API_KEYS):
        masked_key = key[:10] + "..." + key[-4:] if len(key) > 14 else "***"
        stats.append({
            "key_number": i + 1,
            "masked_key": masked_key,
            "total_uses": key_stats[key]["uses"],
            "total_failures": key_stats[key]["failures"],
            "last_failure_seconds_ago": int(time.time() - key_stats[key]["last_failure"]) if key_stats[key]["last_failure"] > 0 else None,
            "status": "available" if time.time() - key_stats[key]["last_failure"] > 60 else "cooling_down"
        })
    
    return {
        "total_keys": len(GROQ_API_KEYS),
        "current_key_index": current_key_index + 1,
        "keys": stats
    }