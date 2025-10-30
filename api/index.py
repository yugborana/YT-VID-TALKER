# /api/index.py

import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from fastapi.responses import JSONResponse

# --- Add python_helpers to the system path ---
# This is a key step for Vercel to find your modules
sys.path.append(os.path.realpath('.'))

# --- Import your helper functions ---
from python_helpers.yt_downloader import download_audio_from_url
from python_helpers.audio_transcribe import audio_main as run_transcription_job
from python_helpers.embed_text import embed_main as run_embedding_pipeline
from python_helpers.blog_generation import generate_blog_post
from python_helpers.rag import setup_pinecone_index, load_and_upsert_data, query_video

# --- Models for API Request/Response ---
class VideoRequest(BaseModel):
    url: str

class QueryRequest(BaseModel):
    query: str

class BlogRequest(BaseModel):
    transcript_file: str

# --- Initialize App and Pinecone ---
app = FastAPI()
pinecone_index = setup_pinecone_index()

# --- CORS Middleware ---
# This allows your Next.js app to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins (you can restrict this in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoint 1: Process Video ---
@app.post("/api/process-video")
async def process_video(request: VideoRequest):
    try:
        print(f"Processing URL: {request.url}")
        
        # 1. Download
        download_audio_from_url(request.url)
        
        # 2. Transcribe
        transcript_file = await run_transcription_job()
        if not transcript_file:
            raise Exception("Transcription failed.")
            
        # 3. Embed
        embedded_file = await run_embedding_pipeline(transcript_file)
        if not embedded_file:
            raise Exception("Embedding failed.")
            
        # 4. Upsert to Pinecone
        load_and_upsert_data(pinecone_index, embedded_file)
        
        print("Pipeline complete!")
        # Return the path to the transcript file for the blog gen
        return {"status": "success", "transcript_file": transcript_file}

    except Exception as e:
        print(f"Error in pipeline: {e}")
        # Return a 500 error
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# --- API Endpoint 2: Ask Question (RAG) ---
@app.post("/api/ask-question")
async def ask_question(request: QueryRequest):
    try:
        answer_stream, contexts = query_video(pinecone_index, request.query)
        
        # We need to collect the streamed response
        final_answer = "".join([chunk for chunk in answer_stream])
            
        return {"answer": final_answer, "contexts": contexts}
        
    except Exception as e:
        print(f"Error in query: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# --- API Endpoint 3: Generate Blog ---
@app.post("/api/generate-blog")
async def generate_blog(request: BlogRequest):
    try:
        blog_post_md = generate_blog_post(request.transcript_file)
        return {"blog_content": blog_post_md}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# Vercel will use this 'app' object to run the server