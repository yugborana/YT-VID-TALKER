"use client"

import type React from "react"
import { useState } from "react"
import { Play, Zap, Lock, Github } from "lucide-react"

export default function Home() {
  const [url, setUrl] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    // Handle video processing here
    setTimeout(() => setIsLoading(false), 1000)
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      <nav className="border-b border-gray-200 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-blue-600 to-indigo-600 p-2 rounded-lg">
              <Play className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">YouTube QA</span>
          </div>
          <a href="#" className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:text-gray-900 transition">
            <Github className="w-5 h-5" />
            <span className="text-sm font-medium">GitHub</span>
          </a>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-20">
        {/* Badge */}
        <div className="flex justify-center mb-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 rounded-full border border-blue-200">
            <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
            <span className="text-sm font-medium text-blue-700">AI-Powered Video Analysis</span>
          </div>
        </div>

        {/* Main Heading */}
        <div className="text-center mb-8">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-4">
            Ask Questions About
            <br />
            <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              Any YouTube Video
            </span>
          </h1>
          <div className="h-1 w-24 bg-gradient-to-r from-blue-600 to-indigo-600 mx-auto mb-8"></div>
        </div>

        {/* Description */}
        <p className="text-center text-lg text-gray-600 mb-4 max-w-2xl mx-auto">
          Get instant answers powered by advanced AI. This app uses{" "}
          <span className="font-semibold text-blue-600">Pinecone</span> for intelligent storage and{" "}
          <span className="font-semibold text-blue-600">Groq</span> for lightning-fast responses.
        </p>
        <p className="text-center text-gray-500 mb-12 max-w-2xl mx-auto">
          Simply paste a YouTube URL and ask any question about the video content.
        </p>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4 mb-12">
          <div>
            <input
              type="url"
              placeholder="https://youtube.com/watch?v=..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="w-full px-6 py-4 bg-white border border-gray-300 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition shadow-sm"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full px-6 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold rounded-xl transition disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
          >
            {isLoading ? "Processing..." : "Process Video"}
          </button>
        </form>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8 border-t border-gray-200">
          <div className="flex flex-col items-center text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-3">
              <Zap className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-1">Lightning Fast</h3>
            <p className="text-sm text-gray-600">Get answers in seconds</p>
          </div>
          <div className="flex flex-col items-center text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-3">
              <Play className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-1">Any Video</h3>
            <p className="text-sm text-gray-600">Works with all YouTube videos</p>
          </div>
          <div className="flex flex-col items-center text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-3">
              <Lock className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-1">Secure</h3>
            <p className="text-sm text-gray-600">Your data is protected</p>
          </div>
        </div>
      </div>
    </main>
  )
}
