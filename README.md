# 🎥 YTVidTalker - AI-Powered Video Analysis & Content Generation

[![Next.js](https://img.shields.io/badge/Next.js-16.0-black?style=flat-square&logo=next.js)](https://nextjs.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-blue?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

> 🚀 Transform YouTube videos into interactive AI experiences with transcription, Q&A, and automated blog generation

## 📺 Demo

Video Demo - [screen-capture.webm](https://github.com/user-attachments/assets/73bf4ca6-7442-4b79-9a61-f4052042ee4f)

<img width="608" height="492" alt="ytvidtalker" src="https://github.com/user-attachments/assets/9ad8c68c-fa21-40e3-8f14-f6b54cf7f262" />

## ✨ Features

### 🎬 Video Processing
- **YouTube Video Download**: Extract audio from any YouTube video using yt-dlp
- **Audio Conversion**: Automatic conversion to 16kHz for optimal transcription quality
- **Intelligent Processing**: Efficient pipeline with cleanup of temporary files

### 📝 AI-Powered Transcription
- **High-Quality Transcription**: Uses Sarvam AI for accurate audio-to-text conversion
- **Cloud Storage**: Leverages Azure Data Lake Storage for scalable file handling
- **Async Processing**: Non-blocking transcription with real-time progress updates

### 🤖 Smart Q&A System
- **RAG Implementation**: Retrieval-Augmented Generation for context-aware responses
- **Vector Search**: Pinecone-powered semantic search through video content
- **Natural Conversations**: Chat interface powered by Groq's LLaMA models
- **Real-time Responses**: Streaming answers with typing indicators

### 📖 Content Generation
- **Automated Blog Posts**: Generate comprehensive blog articles from video transcripts
- **Structured Output**: Well-formatted content with sections and key takeaways
- **Customizable Prompts**: Tailored generation for different content types

### 🎨 Modern UI/UX
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Dark/Light Themes**: Built-in theme toggle with system preference detection
- **Shadcn/ui Components**: Professional, accessible UI components
- **Real-time Feedback**: Loading states, error handling, and success notifications

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js      │    │   FastAPI       │    │   External      │
│   Frontend      │◄──►│   Backend       │◄──►│   Services      │
│                 │    │                 │    │                 │
│ • React 19      │    │ • Python 3.8+   │    │ • YouTube API   │
│ • TypeScript    │    │ • Async Routes  │    │ • Sarvam AI     │
│ • Tailwind CSS  │    │ • CORS Support  │    │ • Azure Storage │
│ • Shadcn/ui     │    │                 │    │ • Groq LLM      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Vector DB     │
                       │   (Pinecone)    │
                       │                 │
                       │ • Embeddings    │
                       │ • Semantic      │
                       │   Search        │
                       └─────────────────┘
```

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js 16 with App Router
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS 4.1.9
- **UI Components**: shadcn/ui with Radix UI primitives
- **State Management**: React Hooks (useState, useEffect)
- **Icons**: Lucide React
- **Forms**: React Hook Form with Zod validation
- **Theme**: next-themes for dark/light mode

### Backend
- **Framework**: FastAPI with async support
- **Language**: Python 3.8+
- **API Documentation**: Automatic OpenAPI/Swagger generation
- **CORS**: Configured for frontend integration
- **Error Handling**: Structured exception management

### AI & Machine Learning
- **LLM**: Groq (LLaMA 3.1 8B Instant)
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Database**: Pinecone for semantic search
- **Transcription**: Sarvam AI with multilingual support
- **Content Generation**: LangChain with Groq integration

### Video & Audio Processing
- **YouTube Download**: yt-dlp with audio extraction
- **Audio Processing**: pydub for format conversion
- **Storage**: Azure Data Lake Storage for file management

### Deployment & Infrastructure
- **Platform**: Vercel Serverless Functions
- **Build Tools**: Next.js build pipeline with Python runtime
- **Environment**: dotenv for configuration management
- **Package Management**: pnpm for frontend, pip for backend

## 📦 Installation

### Prerequisites
- Node.js 18+ 
- Python 3.8+
- pnpm (recommended) or npm
- Git

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ytvidtalker
   ```

2. **Install frontend dependencies**
   ```bash
   pnpm install
   ```

3. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env.local` file in the root directory:
   ```env
   # AI Services
   GROQ_API_KEY=your_groq_api_key
   SARVAM_API_KEY=your_sarvam_api_key
   PINECONE_API_KEY=your_pinecone_api_key

   ```

## 🚀 Usage

### Development Mode
1. **Start the backend**
   ```bash
   uvicorn api.index:app --reload --port 8000
   ```

4. **Start the development server**
   ```bash
   pnpm dev
   ```

5. **Open your browser**
   Navigate to `http://localhost:3000`


## 🔧 API Endpoints

### Process Video
```http
POST /api/process-video
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=example"
}
```

### Query Video Content
```http
POST /api/query
Content-Type: application/json

{
  "query": "What are the main topics discussed?"
}
```

### Generate Blog Post
```http
POST /api/generate-blog
Content-Type: application/json

{
  "transcript_file": "path/to/transcript.json"
}
```

## 📂 Project Structure

```
ytvidtalker/
├── app/                          # Next.js App Router
│   ├── globals.css              # Global styles
│   ├── layout.tsx               # Root layout
│   └── page.tsx                 # Main application page
├── api/                         # FastAPI backend
│   └── index.py                 # Main API server
├── components/                   # React components
│   ├── ui/                      # shadcn/ui components
│   ├── ThemeProvider.tsx        # Theme context
│   └── ThemeToggle.tsx          # Theme switcher
├── python_helpers/              # Backend utilities
│   ├── yt_downloader.py         # YouTube audio extraction
│   ├── audio_transcribe.py      # Sarvam AI transcription
│   ├── embed_text.py           # Text embedding pipeline
│   ├── rag.py                  # RAG implementation
│   └── blog_generation.py      # Content generation
├── hooks/                      # Custom React hooks
├── lib/                        # Utility functions
├── public/                     # Static assets
└── styles/                     # Additional styles
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

### Development Guidelines

- Follow TypeScript and Python best practices
- Use conventional commit messages
- Add tests for new features
- Update documentation as needed
- Ensure code passes linting and type checking

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[Next.js](https://nextjs.org/)** - The React framework for production
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern, fast web framework for building APIs
- **[Groq](https://groq.com/)** - Fast AI inference platform
- **[Sarvam AI](https://sarvam.ai/)** - Indian language AI platform
- **[Pinecone](https://www.pinecone.io/)** - Vector database for similarity search
- **[shadcn/ui](https://ui.shadcn.com/)** - Beautifully designed components
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first CSS framework

<div align="center">
  <p>Made with ❤️ by the YTVidTalker team</p>
  <p>Transforming video content into intelligent conversations</p>
</div>
