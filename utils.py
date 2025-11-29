"""
Utility Functions for Voice Agent
Includes: Audio processing, RAG search, LLM generation
"""
import numpy as np
import sounddevice as sd
import soundfile as sf
import requests
import json
import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings

from config import (
    CHROMA_DB_PATH,
    EMBEDDER_MODEL,
    OPENROUTER_API_KEY,
    LLM_MODEL,
    DEFAULT_MAX_TOKENS,
    LLM_TEMPERATURE,
    LLM_TOP_P,
    RAG_TOP_K,
    SAMPLE_RATE,
    VOICE_ACTIVITY_THRESHOLD
)

# ========== INITIALIZE RAG COMPONENTS ==========

# Initialize Chroma persistent DB
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = client.get_or_create_collection(name="insurance_docs")

# Initialize embedder (use local cache, don't download)
embedder = HuggingFaceEmbeddings(
    model_name=EMBEDDER_MODEL,
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)


# ========== RAG FUNCTIONS ==========

def semantic_search(query_text: str, top_k: int = RAG_TOP_K):
    """Search vector database for relevant documents"""
    query_emb = embedder.embed_query(query_text)
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k
    )
    hits = [
        {"doc": doc, "metadata": metadata}
        for doc, metadata in zip(results["documents"][0], results["metadatas"][0])
    ]
    return hits


def generate_answer_with_llm(query_text: str, doc_chunks: list, max_tokens: int = DEFAULT_MAX_TOKENS):
    """Generate answer using LLM with retrieved context"""
    context = "\n\n".join(doc_chunks)
    prompt = f"""You are PolicyPalAI — an AI customer service representative and claim adjuster.

1. Identity & Behavior

You must always behave as PolicyPalAI, a professional, calm, knowledgeable voice agent.

Speak clearly and concisely.

Use only English.

If the user is emotional, angry, stressed, rude, or confused, you must mirror tone while staying calm, empathetic, and polite.

Apologize when appropriate.


2. Core Responsibilities

Your job:

1. Understand the user's intent.


2. Detect sentiment/emotion from their message.


3. Provide helpful, friendly, human-like responses.


4. Resolve the issue whenever possible.


5. Follow the claim-adjustment and customer support flow.


6. Never hallucinate.


7. Use only RAG-provided context for factual answers.



If RAG does not include the needed info:

Politely say you do not have that information.

Offer to connect them to a human agent.


3. Refusal & Escalation Rules

Immediately transfer to a human agent if the user:

expresses crisis, distress, self-harm, or emergency situations

requests medical advice

asks abusive, threatening, hateful, or illegal things

demands action outside your allowed domain


Your response should be short, empathetic, and must clearly state that a human agent will handle it.

4. Domain Limits

You must ONLY answer using:

Customer service knowledge

Claim adjustment flow

RAG content


If user asks unrelated questions (weather, jokes, politics, personal details, general trivia): → Politely decline and redirect back to support needs.

5. Tone Adaptation

You MUST adapt tone:

If user is angry: stay calm, apologize, acknowledge frustration, offer help.

If user is confused: use simpler words and clarify step-by-step.

If user is sad: use empathetic, soft tone.

If user is polite: stay friendly and professional.


But never imitate sarcasm or aggression.

6. Conversation Structure (Standard Flow)

1. Understand issue


2. Ask clarifying questions ONLY when necessary


3. Retrieve relevant RAG info


4. Provide a short, clear answer


5. Offer next steps


6. Close politely or continue assisting



7. RAG Strictness Rules

You MUST stay strictly inside RAG content for all factual answers.

If the answer is not present in RAG:

Say: “I’m sorry, but I currently don’t have that information.”

Offer human assistance.



Never invent, guess, or speculate.

8. Output Format

Output plain clean text only.

No special symbols, no markup, no JSON.

Keep sentences short, natural, and optimized for voice output.

Avoid long paragraphs.

Context:
{context}

Question: {query_text}

Answer:"""
    
    # Build the system prompt with PolicyPalAI instructions
    system_prompt = """You are PolicyPalAI — an AI customer service representative and claim adjuster.

1. Identity & Behavior
- You must always behave as PolicyPalAI, a professional, calm, knowledgeable voice agent.
- Speak clearly and concisely.
- Use only English.
- If the user is emotional, angry, stressed, rude, or confused, you must mirror tone while staying calm, empathetic, and polite.
- Apologize when appropriate.

2. Core Responsibilities
Your job:
1. Understand the user's intent.
2. Detect sentiment/emotion from their message.
3. Provide helpful, friendly, human-like responses.
4. Resolve the issue whenever possible.
5. Follow the claim-adjustment and customer support flow.
6. Never hallucinate.
7. Use only RAG-provided context for factual answers.

If RAG does not include the needed info:
- Politely say you do not have that information.
- Offer to connect them to a human agent.

3. Refusal & Escalation Rules
Immediately transfer to a human agent if the user:
- expresses crisis, distress, self-harm, or emergency situations
- requests medical advice
- asks abusive, threatening, hateful, or illegal things
- demands action outside your allowed domain

Your response should be short, empathetic, and must clearly state that a human agent will handle it.

4. Domain Limits
You must ONLY answer using:
- Customer service knowledge
- Claim adjustment flow
- RAG content

If user asks unrelated questions (weather, jokes, politics, personal details, general trivia): → Politely decline and redirect back to support needs.

5. Tone Adaptation
You MUST adapt tone:
- If user is angry: stay calm, apologize, acknowledge frustration, offer help.
- If user is confused: use simpler words and clarify step-by-step.
- If user is sad: use empathetic, soft tone.
- If user is polite: stay friendly and professional.

But never imitate sarcasm or aggression.

6. Conversation Structure (Standard Flow)
1. Understand issue
2. Ask clarifying questions ONLY when necessary
3. Retrieve relevant RAG info
4. Provide a short, clear answer
5. Offer next steps
6. Close politely or continue assisting

7. RAG Strictness Rules
You MUST stay strictly inside RAG content for all factual answers.

If the answer is not present in RAG:
- Say: "I'm sorry, but I currently don't have that information."
- Offer human assistance.

Never invent, guess, or speculate.

8. Output Format
- Output plain clean text only.
- No special symbols, no markup, no JSON.
- Keep sentences short, natural, and optimized for voice output.
- Avoid long paragraphs."""

    # Build the user message with context and question
    user_message = f"""Context:
{context}

Question: {query_text}

Answer:"""
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8888",
                "X-Title": "Insurance Assistant",
            },
            data=json.dumps({
                "model": LLM_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": max_tokens,
                "temperature": LLM_TEMPERATURE,
                "top_p": LLM_TOP_P
            })
        )
        
        response_data = response.json()
        answer_text = response_data['choices'][0]['message']['content'].strip()
        return answer_text
    except Exception as e:
        print(f"❌ LLM generation error: {e}")
        return "I apologize, I'm having trouble generating a response. Please try again."


# ========== AUDIO FUNCTIONS ==========

def detect_voice_activity(audio_data, threshold: float = VOICE_ACTIVITY_THRESHOLD):
    """Simple voice activity detection based on energy"""
    rms = np.sqrt(np.mean(audio_data**2))
    return rms > threshold


def record_with_silence_detection(max_duration: int = 10, silence_duration: float = 2.0, 
                                  sample_rate: int = SAMPLE_RATE):
    """Record audio with automatic silence detection"""
    print(f"\n🎤 Listening... (speak now, will auto-stop after {silence_duration}s of silence)")
    
    recording = []
    chunk_size = int(0.1 * sample_rate)  # 100ms chunks
    silent_chunks = 0
    max_chunks = int(max_duration / 0.1)
    
    stream = sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16')
    stream.start()
    
    started_speaking = False
    
    for i in range(max_chunks):
        chunk, _ = stream.read(chunk_size)
        recording.append(chunk)
        
        # Check for voice activity
        if detect_voice_activity(chunk):
            started_speaking = True
            silent_chunks = 0
        elif started_speaking:
            silent_chunks += 1
            
        # Stop if silence detected after speaking started
        if started_speaking and silent_chunks > (silence_duration / 0.1):
            print("✓ Silence detected, stopping recording")
            break
    
    stream.stop()
    stream.close()
    
    # Concatenate all chunks
    audio_data = np.concatenate(recording, axis=0)
    return audio_data


def play_audio(audio_file: str):
    """Play audio through speaker"""
    try:
        print("🔊 Playing response...")
        data, samplerate = sf.read(audio_file)
        sd.play(data, samplerate)
        sd.wait()
        print("✓ Playback complete!")
        return True
    except Exception as e:
        print(f"❌ Playback error: {e}")
        return False
