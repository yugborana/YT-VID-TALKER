# rag_pinecone.py

import os
import json
import time
from dotenv import load_dotenv

import pinecone
from groq import Groq
from sentence_transformers import SentenceTransformer
from typing import Generator

# --- 1. INITIALIZATION ---

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not PINECONE_API_KEY or not GROQ_API_KEY:
    raise ValueError("PINECONE_API_KEY and GROQ_API_KEY must be set in the .env file")

# Initialize clients
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# --- 2. CONFIGURATION ---
PINECONE_INDEX_NAME = "youtube-transcript-rag"
MODEL_DIMENSION = 384
GROQ_LLM_MODEL = "llama-3.1-8b-instant"

def convert_to_timestamp(seconds: float) -> str:
    """Converts seconds to a HH:MM:SS timestamp format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

# --- 3. CORE PINECODE FUNCTIONS ---

def setup_pinecone_index():
    """Checks if the Pinecone index exists and creates it if it doesn't."""
    if PINECONE_INDEX_NAME not in pc.list_indexes().names():
        print(f"Index '{PINECONE_INDEX_NAME}' not found. Creating it...")
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=MODEL_DIMENSION,
            metric='cosine',
            spec=pinecone.ServerlessSpec(cloud='aws', region='us-east-1')
        )
        print("Waiting for index to initialize...")
        time.sleep(15)
    
    return pc.Index(PINECONE_INDEX_NAME)

def load_and_upsert_data(index, filepath: str):
    """Loads data from the JSON file and upserts it into the Pinecone index."""
    stats = index.describe_index_stats()
    if stats['total_vector_count'] > 0:
        print("Index already contains data. Clearing existing vectors...")
        index.delete(delete_all=True)
        print("Waiting for index to clear...")
        time.sleep(10)

    try:
        with open(filepath, "r") as f:
            transcript_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {filepath} was not found.")
        return False

    entries = transcript_data.get("diarized_transcript", {}).get("entries", [])
    vectors_to_upsert = []
    for i, entry in enumerate(entries):
        if "embedding" in entry and "transcript" in entry:
            metadata = {
                "text": entry["transcript"],
                "speaker": entry.get("speaker_id", "Unknown"),
                "start": entry.get("start_time_seconds", 0),
                "end": entry.get("end_time_seconds", 0)
            }
            vectors_to_upsert.append({
                "id": f"entry_{i}",
                "values": entry["embedding"],
                "metadata": metadata
            })

    if not vectors_to_upsert:
        print("No vectors to upsert.")
        return False

    print(f"Upserting {len(vectors_to_upsert)} vectors to Pinecone index...")
    for i in range(0, len(vectors_to_upsert), 100):
        batch = vectors_to_upsert[i:i+100]
        index.upsert(vectors=batch)
    
    print("Upsert complete. Waiting for index to update...")
    time.sleep(10)
    return True

def get_groq_response_streamed(query: str, context: str) -> Generator[str, None, None]:
    """Generates a streaming answer from Groq based on query and context."""
    
    system_prompt = """
    You are a helpful assistant who answers questions based on the provided video transcript context.
    - Answer the question directly using only the information from the CONTEXT below.
    - Cite the context you are using by referencing its number, like `[0]`, `[1]`, etc.
    - If the context does not contain the answer, state "I cannot answer this question based on the provided transcript.
    """ # Your system prompt remains the same
    user_prompt = f"CONTEXT:\n{context}\n\nQUESTION:\n{query}"

    try:
        stream = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model=GROQ_LLM_MODEL,
            temperature=0.2,
            stream=True, # Enable streaming
        )
        
        # Yield each chunk of content as it arrives
        for chunk in stream:
            if content := chunk.choices[0].delta.content:
                yield content

    except Exception as e:
        yield f"An error occurred while generating a response from Groq: {e}"

# --- 4. RAG QUERY FUNCTIONS ---

def query_video(index, query: str, top_k: int = 5):
    """Retrieves context and calls the streaming generator for the answer."""
    # 1. Retrieve context from Pinecone (this part is unchanged)
    query_embedding = model.encode(query).tolist()
    query_result = index.query(
        vector=query_embedding, top_k=top_k, include_metadata=True
    )
    matches = query_result.get('matches', [])
    if not matches:
        def empty_stream():
            yield "I could not find relevant information in the transcript."
        return empty_stream(), []

    # 2. Format contexts (this part is unchanged)
    contexts_for_llm = []
    contexts_for_display = []
    for i, match in enumerate(matches):
        metadata = match['metadata']
        text = metadata.get('text', '')
        start_time = metadata.get('start', 0)
        end_time = metadata.get('end', 0)
        source_tag = f"Timestamp: [{convert_to_timestamp(start_time)} - {convert_to_timestamp(end_time)}]"
        contexts_for_llm.append(f"Context [{i}] ({source_tag}):\n{text}")
        contexts_for_display.append(f"Speaker {metadata.get('speaker', 'Unknown')}: \"{text}\"\n*({source_tag})*")

    # 3. Call the streaming generator and return it
    answer_stream = get_groq_response_streamed(query, " ".join(contexts_for_llm))
    
    return answer_stream, contexts_for_display