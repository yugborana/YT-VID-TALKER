// /app/page.tsx (Updated)
"use client";

import type React from "react";
import { useState, useEffect } from "react";
import { Play, Zap, Lock, Github, Loader2, CheckCircle2, AlertTriangle, BookMarked, Sparkles, Send } from "lucide-react";

// Import necessary shadcn/ui components (ensure these paths match your structure)
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { useToast } from "@/hooks/use-toast"; // Assuming you added the Toast hook
import { ThemeToggle } from "@/components/ThemeToggle"; // Assuming you created ThemeToggle

// Define the structure for a chat message
interface Message {
  role: "user" | "ai";
  content: string;
}

export default function Home() {
  const [url, setUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false); // For processing video
  const [error, setError] = useState<string | null>(null);
  const [videoProcessed, setVideoProcessed] = useState(false);
  const [transcriptFilePath, setTranscriptFilePath] = useState<string | null>(null); // To store the path for blog gen

  const [question, setQuestion] = useState("");
  const [isAnswering, setIsAnswering] = useState(false); // For answering questions
  const [chatHistory, setChatHistory] = useState<Message[]>([]);

  const [blogContent, setBlogContent] = useState("");
  const [isGeneratingBlog, setIsGeneratingBlog] = useState(false); // For blog generation

  const { toast } = useToast();

  // --- API Call Handlers ---

  const handleProcessVideo = async (e?: React.FormEvent) => {
    e?.preventDefault(); // Prevent form submission if called from form
    if (!url) {
      setError("Please enter a YouTube URL.");
      toast({ variant: "destructive", title: "Missing URL", description: "Please enter a YouTube URL." });
      return;
    }
    setIsLoading(true);
    setError(null);
    setVideoProcessed(false);
    setChatHistory([]); // Clear previous chat
    setTranscriptFilePath(null); // Clear previous transcript path

    try {
      const response = await fetch("http://localhost:8000/api/process-video", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || `HTTP error! status: ${response.status}`);
      }
      
      if (data.status !== "success") {
         throw new Error(data.message || "Backend processing failed.");
      }

      setVideoProcessed(true);
      setTranscriptFilePath(data.transcript_file); // Store the path
      toast({
        title: "Success!",
        description: "Video processed. You can now ask questions or generate a blog post.",
      });

    } catch (err: any) {
      console.error("Processing Error:", err);
      const errorMessage = err.message || "An unknown error occurred during processing.";
      setError(errorMessage);
      toast({
        variant: "destructive",
        title: "Processing Failed",
        description: errorMessage,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAskQuestion = async () => {
    if (!question || isAnswering) return;

    setIsAnswering(true);
    const userMessage: Message = { role: "user", content: question };
    // Optimistically add user message
    setChatHistory((prev) => [...prev, userMessage]); 
    const currentQuestion = question; // Capture current question before clearing
    setQuestion(""); 

    try {
      const response = await fetch("http://localhost:8000/api/ask-question", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: currentQuestion }), // Use captured question
      });
      
      const data = await response.json();
       if (!response.ok) {
        throw new Error(data.answer || `HTTP error! status: ${response.status}`);
      }
      
      const aiMessage: Message = { role: "ai", content: data.answer };
      setChatHistory((prev) => [...prev, aiMessage]);

    } catch (err: any) {
       console.error("Answering Error:", err);
       const errorMessageContent = "Sorry, I had trouble finding an answer. " + (err.message || "Unknown error.");
      const errorMessage: Message = {
        role: "ai",
        content: errorMessageContent,
      };
      // Add error message to chat
      setChatHistory((prev) => [...prev, errorMessage]); 
       toast({
        variant: "destructive",
        title: "Error Getting Answer",
        description: err.message || "Unknown error.",
      });
    } finally {
      setIsAnswering(false);
    }
  };

   const handleGenerateBlog = async () => {
     if (!transcriptFilePath) {
        setError("Transcript file path is missing. Cannot generate blog.");
        toast({ variant: "destructive", title: "Error", description: "Transcript file not found." });
        return;
     }
    setIsGeneratingBlog(true);
    setBlogContent("");
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/api/generate-blog", {
         method: "POST",
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({ transcript_file: transcriptFilePath }), // Send the path
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.blog_content || `HTTP error! status: ${response.status}`);
      }

      setBlogContent(data.blog_content);
       toast({
        title: "Blog Post Generated!",
        description: "The blog post has been created successfully.",
      });

    } catch (err: any) {
       console.error("Blog Generation Error:", err);
       const errorMsg = "Sorry, I had trouble generating the blog post. " + (err.message || "Unknown error.");
      setBlogContent(errorMsg); // Show error in the sheet
       toast({
        variant: "destructive",
        title: "Blog Generation Failed",
        description: err.message || "Unknown error.",
      });
    } finally {
      setIsGeneratingBlog(false);
    }
  };


  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-slate-900 dark:via-black dark:to-slate-800 text-gray-900 dark:text-gray-100">
      {/* --- Navigation --- */}
      <nav className="border-b border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-black/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-blue-600 to-indigo-600 p-2 rounded-lg">
              <Play className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold">YouTube QA</span>
          </div>
          <div className="flex items-center gap-4">
             <a href="https://github.com/yugborana/yt-vid-talker" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 px-4 py-2 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition">
               <Github className="w-5 h-5" />
               <span className="text-sm font-medium hidden sm:inline">GitHub</span>
             </a>
            <ThemeToggle />
          </div>
        </div>
      </nav>

      {/* --- Main Content Area --- */}
      <div className="max-w-4xl mx-auto px-6 py-12 md:py-20">
        {/* Badge */}
        <div className="flex justify-center mb-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 dark:bg-blue-900/50 rounded-full border border-blue-200 dark:border-blue-700">
            <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
            <span className="text-sm font-medium text-blue-700 dark:text-blue-300">AI-Powered Video Analysis</span>
          </div>
        </div>

        {/* Heading */}
        <div className="text-center mb-8">
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold mb-4">
            Ask Questions About
            <br />
            <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              Any YouTube Video
            </span>
          </h1>
          <div className="h-1 w-24 bg-gradient-to-r from-blue-600 to-indigo-600 mx-auto mb-8"></div>
        </div>

        {/* Description */}
        <p className="text-center text-lg text-gray-600 dark:text-gray-400 mb-4 max-w-2xl mx-auto">
          Get instant answers powered by advanced AI. This app uses{" "}
          <span className="font-semibold text-blue-600 dark:text-blue-400">Pinecone</span> for intelligent storage and{" "}
          <span className="font-semibold text-blue-600 dark:text-blue-400">Groq</span> for lightning-fast responses.
        </p>
        <p className="text-center text-gray-500 dark:text-gray-500 mb-12 max-w-2xl mx-auto">
          Simply paste a YouTube URL and ask any question about the video content.
        </p>

        {/* --- URL Input Form --- */}
        <form onSubmit={handleProcessVideo} className="space-y-4 mb-12">
          <div>
            {/* Using shadcn Input */}
            <Input
              type="url"
              placeholder="https://youtube.com/watch?v=..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="w-full px-6 py-4 text-base bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 rounded-xl placeholder-gray-400 dark:placeholder-gray-500 focus:ring-blue-500 focus:border-blue-500 transition shadow-sm h-14" // Increased height
              disabled={isLoading}
            />
          </div>

          {/* Using shadcn Button */}
          <Button
            type="submit"
            disabled={isLoading}
            className="w-full px-6 py-4 text-base font-semibold rounded-xl transition shadow-lg hover:shadow-xl h-14 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50" // Increased height
          >
            {isLoading ? (
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            ) : (
              <Sparkles className="mr-2 h-5 w-5" />
            )}
            {isLoading ? "Processing..." : "Process Video"}
          </Button>
        </form>

        {/* --- Alerts --- */}
        {error && !isLoading && (
            <Alert variant="destructive" className="mb-8">
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

        {videoProcessed && (
          <Alert variant="default" className="mb-8 border-green-500 bg-green-500/10 text-green-700 dark:text-green-400 dark:border-green-700">
            <CheckCircle2 className="h-4 w-4 text-green-500" />
            <AlertTitle className="text-green-700 dark:text-green-500 font-semibold">Video Processed!</AlertTitle>
            <AlertDescription>
              You can now ask questions or generate a blog post below.
            </AlertDescription>
          </Alert>
        )}


        {/* --- Q&A and Blog Section (Conditional) --- */}
        {videoProcessed && (
          <Card className="overflow-hidden shadow-lg mt-12 bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
            <CardContent className="p-6 space-y-8">

              {/* Blog Generator Button & Sheet */}
              <Sheet>
                  <SheetTrigger asChild>
                    <Button
                      variant="outline"
                      onClick={handleGenerateBlog} // Call the specific handler
                      disabled={isGeneratingBlog}
                      className="dark:text-gray-100 dark:border-gray-600 dark:hover:bg-gray-700"
                    >
                      {isGeneratingBlog ? (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      ) : (
                        <BookMarked className="mr-2 h-4 w-4" />
                      )}
                      Generate Blog Post
                    </Button>
                  </SheetTrigger>
                  <SheetContent className="w-[600px] sm:max-w-none bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 border-gray-200 dark:border-gray-700">
                    <SheetHeader>
                      <SheetTitle>Generated Blog Post</SheetTitle>
                      <SheetDescription className="dark:text-gray-400">
                        Here is a blog post generated from the video content.
                      </SheetDescription>
                    </SheetHeader>
                    <div className="prose dark:prose-invert py-4 max-h-[80vh] overflow-y-auto mt-4 border-t dark:border-gray-700 pt-4">
                      {isGeneratingBlog ? (
                        <div className="flex items-center justify-center p-8">
                          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                          <p className="ml-4">Generating...</p>
                        </div>
                      ) : (
                        // Use pre-wrap to respect newlines from the markdown
                        <pre className="whitespace-pre-wrap font-sans text-sm dark:text-gray-300">
                          {blogContent || "Click 'Generate Blog Post' to create content."}
                        </pre>
                      )}
                    </div>
                  </SheetContent>
                </Sheet>

              {/* Chat Interface */}
              <div className="space-y-4">
                <h3 className="text-xl font-semibold border-b pb-2 dark:border-gray-700">Ask a Question</h3>
                {/* Chat History */}
                <div className="space-y-4 rounded-md border dark:border-gray-700 p-4 h-80 overflow-y-auto bg-gray-50 dark:bg-gray-900/50">
                  {chatHistory.length === 0 ? (
                    <p className="text-sm text-gray-500 dark:text-gray-400 text-center pt-4">
                      Ask a question about the video content.
                    </p>
                  ) : (
                    chatHistory.map((msg, index) => (
                      <div
                        key={index}
                        className={`flex ${
                          msg.role === "user" ? "justify-end" : "justify-start"
                        }`}
                      >
                        <div
                          className={`max-w-[85%] rounded-lg px-4 py-2 shadow-sm ${
                            msg.role === "user"
                              ? "bg-blue-600 text-white"
                              : "bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                          }`}
                        >
                          {/* Basic markdown rendering can be added here if needed */}
                          {msg.content}
                        </div>
                      </div>
                    ))
                  )}
                  {isAnswering && (
                     <div className="flex justify-start">
                        <div className="bg-gray-200 dark:bg-gray-700 rounded-lg px-4 py-2 inline-flex items-center shadow-sm">
                           <Loader2 className="h-5 w-5 animate-spin text-gray-500 dark:text-gray-400" />
                        </div>
                     </div>
                  )}
                </div>

                {/* Chat Input */}
                <div className="flex gap-2 pt-4 border-t dark:border-gray-700">
                  <Input
                    type="text"
                    placeholder="What are the key topics discussed?"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && !isAnswering && handleAskQuestion()}
                    disabled={isAnswering}
                    className="flex-1 bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 rounded-lg h-11"
                  />
                  <Button onClick={handleAskQuestion} disabled={isAnswering || !question} className="h-11 bg-blue-600 hover:bg-blue-700">
                    <Send className="h-5 w-5" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* --- Feature Highlights (Your original section) --- */}
        {!videoProcessed && (
           <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-12 mt-12 border-t border-gray-200 dark:border-gray-700">
             <div className="flex flex-col items-center text-center p-4 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800/50 transition">
               <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/50 rounded-lg flex items-center justify-center mb-3">
                 <Zap className="w-6 h-6 text-blue-600 dark:text-blue-400" />
               </div>
               <h3 className="font-semibold mb-1">Lightning Fast</h3>
               <p className="text-sm text-gray-600 dark:text-gray-400">Get answers in seconds</p>
             </div>
             <div className="flex flex-col items-center text-center p-4 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800/50 transition">
               <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/50 rounded-lg flex items-center justify-center mb-3">
                 <Play className="w-6 h-6 text-blue-600 dark:text-blue-400" />
               </div>
               <h3 className="font-semibold mb-1">Any Video</h3>
               <p className="text-sm text-gray-600 dark:text-gray-400">Works with all YouTube videos</p>
             </div>
             <div className="flex flex-col items-center text-center p-4 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800/50 transition">
               <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/50 rounded-lg flex items-center justify-center mb-3">
                 <Lock className="w-6 h-6 text-blue-600 dark:text-blue-400" />
               </div>
               <h3 className="font-semibold mb-1">Secure</h3>
               <p className="text-sm text-gray-600 dark:text-gray-400">Your data is protected</p>
             </div>
           </div>
        )}
      </div>
    </main>
  );
}
