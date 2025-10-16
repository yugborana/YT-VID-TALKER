import time
import re
import json
from dotenv import load_dotenv

# LangChain Imports
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

load_dotenv()

# --- LangChain Model Initialization ---
# Initialize the model once for the entire module for efficiency
llm = ChatGroq(model_name="llama-3.1-8b-instant", temperature=0.2)


def clean_section(text: str) -> str:
    """Remove generic phrases from model output."""
    text = re.sub(r"^Sure,? (here( is|'s| are))?[^\n]*:?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^Here( is|'s| are)?[^\n]*:?\s*", "", text, flags=re.IGNORECASE)
    return text.strip()

def read_transcript(file_path: str) -> str | None:
    """Reads a JSON file and extracts the 'transcript' field."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("transcript")
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"❌ Error: Could not read or find the file at {file_path}")
        return None

def generate_blog_post(transcript_file_path: str) -> str:
    """Generate a concise blog post from a transcript file using LangChain."""
    transcript_text = read_transcript(transcript_file_path)
    if not transcript_text:
        return "Error: Could not read or find the transcript text."

    # 1. Split the text and create LangChain Document objects
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    docs = [Document(page_content=chunk) for chunk in text_splitter.split_text(transcript_text)]
    
    # 2. Use LangChain's Map-Reduce chain to get a condensed summary
    # This replaces the manual for-loop and time.sleep(), solving the rate limit error.
    print(f"Summarizing content using LangChain ({len(docs)} documents)...")
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    condensed_context = chain.invoke(docs, return_only_outputs=True)['output_text']
    print("Content summarized. Generating final blog post components...")

    # 3. Generate the final blog components from the high-quality summary
    # We use the same LLM instance for these final, less frequent calls.
    prompt_templates = {
        "title": (
            "You are a professional blog writer. Generate ONLY a title, no explanations or options. "
            "Create a clear, engaging blog title that captures the main value. "
            "Focus on the key benefit or solution. "
            f"Keep it under 60 characters.\n\n{condensed_context}\n\nTitle:"
        ),
        "outline": (
            "You are a professional blog writer. Generate ONLY the headings, no explanations or options. "
            "Create 5 clear headings that tell a story:\n"
            "1. Introduction (hook and context)\n"
            "2. The Challenge (what's the problem)\n"
            "3. The Solution (how to solve it)\n"
            "4. Key Takeaways (main points to remember)\n"
            "5. Conclusion (what's next)\n\n"
            f"Keep headings clear and direct.\n\n{condensed_context}\n\nOutline:"
        ),
        "section": (
            "You are a professional blog writer. Generate ONLY the section content, no explanations or options. "
            "Keep it clear and practical. "
            "Use simple examples where helpful. "
            "Aim for 2-3 paragraphs.\n\n"
            f"Context:\n{condensed_context}\n\nSection:"
        ),
        "summary": (
            "You are a professional blog writer. Generate ONLY the summary, no explanations or options. "
            "Write a brief 100-word summary that captures the main points. "
            "Keep it simple and actionable.\n\n"
            f"Content:\n\n{condensed_context}\n\nSummary:"
        ),
        "chunk_summary": (
            "You are a professional blog writer. Generate ONLY the summary, no explanations or options. "
            "Extract the key points and main ideas. "
            f"Focus on practical insights.\n\n{condensed_context}\n\nSummary:"
        )
    }
    
    title = llm.invoke(prompt_templates["title"]).content.strip()
    outline_raw = llm.invoke(prompt_templates["outline"]).content.strip()
    headings = [line.strip("-•12345. \n") for line in outline_raw.split("\n") if line.strip()]

    sections = []
    for heading in headings:
        prompt = prompt_templates["section"].format(heading=heading)
        section_content = llm.invoke(prompt).content
        cleaned_section = clean_section(section_content)
        sections.append(f"### {heading}\n{cleaned_section}")
        time.sleep(2)

    full_content = "\n\n".join(sections)
    summary_prompt = prompt_templates["summary"].format(full_content=full_content)
    summary = llm.invoke(summary_prompt).content.strip()

    # 4. Assemble the final blog post
    cta_section = (
        "\n\n---\n\n"
        "## Ready to Learn More?\n\n"
        "1. Share this article with your network\n"
        "2. Leave a comment with your thoughts\n"
        "3. Subscribe for more insights"
    )
    
    blog_post = f"# {title}\n\n{full_content}\n\n**Summary:**\n{summary}\n{cta_section}"
    
    return blog_post







