# app.py

import streamlit as st
import os
import asyncio
from dotenv import load_dotenv

# --- Import functions from your project files ---
# Local processing pipeline
from yt_downloader import download_audio_from_url
from audio_transcribe import audio_main as run_transcription_job
from embed_text import embed_main as run_embedding_pipeline
from blog_generation import generate_blog_post

# NEW: Import the Pinecone RAG functions
from rag import setup_pinecone_index, load_and_upsert_data, query_video

# --- Page Configuration ---
st.set_page_config(page_title="YTVidTalker", page_icon="🎙️", layout="wide")

# --- Load API Keys ---
load_dotenv()
# Note: Pinecone and Groq keys are loaded within rag_pinecone.py

# --- App State Management ---
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False

# --- Helper Functions & Backend Initialization ---
@st.cache_resource
def initialize_pinecone():
    """Initializes and returns the Pinecone index object."""
    try:
        return setup_pinecone_index()
    except Exception as e:
        st.error(f"Failed to initialize Pinecone: {e}")
        return None

def process_video_pipeline(url, index):
    """Orchestrates the entire video processing pipeline."""
    with st.spinner("Step 1/4: Downloading audio from YouTube... 📥"):
        try:
            download_audio_from_url(url)
            st.success("Audio downloaded!")
        except Exception as e:
            st.error(f"Failed to download audio: {e}"); return False

    with st.spinner("Step 2/4: Transcribing audio... ✍️"):
        transcript_file = asyncio.run(run_transcription_job())
        if transcript_file:
            st.session_state.transcript_file = transcript_file 
            st.success("Audio transcribed!")
        else: st.error("Audio transcription failed."); return False

    with st.spinner("Step 3/4: Generating text embeddings... 🧠"):
        embedded_file = asyncio.run(run_embedding_pipeline(transcript_file))
        if embedded_file: st.success("Embeddings generated!")
        else: st.error("Embedding generation failed."); return False
    
    with st.spinner("Step 4/4: Storing data in Pinecone... 🌲"):
        success = load_and_upsert_data(index, embedded_file)
        if success: st.success("Data stored in Pinecone successfully!")
        else: st.error("Failed to store data in Pinecone."); return False
    
    return True

# --- Main Application UI ---
st.title("🎙️ YouTube Video Question Answering")
st.markdown("Ask questions about any YouTube video! This app uses **Pinecone** for storage and **Groq** for fast answers.")

# Initialize Pinecone Index
pinecone_index = initialize_pinecone()
if not pinecone_index:
    st.error("Application cannot start due to Pinecone connection issues. Check your API keys and configuration.")
    st.stop()

url = st.text_input("Enter YouTube URL:", placeholder="https://youtube.com/...")

if st.button("Process Video", type="primary"):
    if url:
        # Run the full pipeline
        pipeline_success = process_video_pipeline(url, pinecone_index)
        if pipeline_success:
            st.session_state.processing_complete = True
            # Use rerun to ensure the UI updates correctly after processing
            st.rerun()
    else:
        st.warning("Please enter a YouTube URL to begin.")

if st.session_state.processing_complete:
    st.success("Video processed! You can now ask questions or generate a blog post.")
    
    if st.button("📝 Generate Blog Post", type="secondary"):
        with st.spinner("Generating your blog post... this may take a moment!"):
            transcript_path = st.session_state.get("transcript_file")
        
        if transcript_path:
            # 2. Call the main generator function from your other file
            blog_post_md = generate_blog_post(transcript_path)
            
            # 3. Store the result in session state to display it
            st.session_state.blog_content = blog_post_md
            st.write(blog_post_md)
        else:
            st.error("Could not find the transcript file needed to generate the blog.")

    st. divider()
    st.subheader("💬 Ask a Question")
    
    query = st.text_input("Ask a question about the video:", placeholder="What are the key topics discussed?")

    if query:
        with st.spinner("Finding relevant contexts and generating an answer..."):
            # Call the single, unified query function
            final_answer, retrieved_contexts = query_video(pinecone_index, query)
            
            st.divider()
            st.subheader("Final Answer")
            st.write_stream(final_answer)

            with st.expander("Show Relevant Contexts"):
                for context in retrieved_contexts:
                    st.info(context)