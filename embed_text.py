import asyncio
import json
from sentence_transformers import SentenceTransformer

print("Loading sentence-transformer model...")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print("Model loaded.")

async def embed(texts: list[str]) -> list[list[float]]:
    embeddings = await asyncio.to_thread(model.encode, texts)
    return embeddings.tolist()

async def embed_transcript(transcript: dict) -> dict:
    entries = transcript["diarized_transcript"]["entries"]
    texts = [entry["transcript"] for entry in entries]
    embeddings = await embed(texts)
    
    for i, emb in enumerate(embeddings):
        transcript["diarized_transcript"]["entries"][i]["embedding"] = emb
        
    return transcript

async def embed_main(transcript_filepath: str) -> str | None:
    """Reads a JSON file, adds embeddings, and saves to a new file."""
    if not transcript_filepath:
        return None  
    output_filepath = "0_embedded_gemini.json"
    
    with open(transcript_filepath, "r") as f:
        transcript = json.load(f)
        
    transcript = await embed_transcript(transcript)
    
    with open(output_filepath, "w") as f:
        json.dump(transcript, f, indent=2)
        
    print(f"Saved to {output_filepath}")
    return output_filepath


if __name__ == "__main__":
    asyncio.run(embed_main())


    