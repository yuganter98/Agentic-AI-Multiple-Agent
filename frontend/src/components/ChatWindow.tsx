"use client";
import { useState, useRef, useEffect } from "react";
import { ChatMessage } from "../types/agent";
import { submitTask } from "../services/api";
import { MessageBubble } from "./MessageBubble";
import { QueryInput } from "./QueryInput";
import { AgentSteps } from "./AgentSteps";
import { MetricsDashboard } from "./MetricsDashboard";
import { motion } from "framer-motion";
import { Bot, Sparkles } from "lucide-react";

export function ChatWindow() {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isProcessing, setIsProcessing] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom of chat when messages change
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTo({
                top: scrollRef.current.scrollHeight,
                behavior: "smooth"
            });
        }
    }, [messages, isProcessing]);

    const handleSend = async (content: string) => {
        // ... (Send handler omitted for brevity, unchanged)
        const userMsg: ChatMessage = {
            id: Date.now().toString(),
            role: "user",
            content,
        };
        setMessages((prev) => [...prev, userMsg]);
        setIsProcessing(true);

        try {
            const response = await submitTask(content);
            const aiMsg: ChatMessage = {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content: response.final_answer?.summary || "Completed task.",
                metadata: response,
            };
            setMessages((prev) => [...prev, aiMsg]);
        } catch (error: any) {
            const errorMsg: ChatMessage = {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content: "Failed to process task.",
                error: error.message || "Unknown error occurred.",
            };
            setMessages((prev) => [...prev, errorMsg]);
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <div className="flex flex-col h-screen w-full bg-transparent text-zinc-100 overflow-hidden font-sans">

            {/* Header - Floating Glass Pill */}
            <header className="flex-shrink-0 pt-6 px-4 md:px-8 z-20 flex justify-center">
                <motion.div 
                    initial={{ y: -20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    className="glass-pill rounded-full px-5 py-3 flex items-center gap-4 w-full max-w-4xl"
                >
                    <div className="h-9 w-9 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center font-bold text-white shadow-lg text-lg ring-2 ring-blue-500/20">
                        <Sparkles size={18} />
                    </div>
                    <div className="flex-1 flex items-center justify-between">
                        <div>
                            <h1 className="text-[15px] font-bold tracking-wide text-zinc-100 uppercase">Agentic AI</h1>
                            <div className="flex items-center gap-2 text-[11px] font-medium text-zinc-400 mt-0.5">
                                <span className="relative flex h-2 w-2">
                                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                                </span>
                                SYSTEM ONLINE
                            </div>
                        </div>
                    </div>
                </motion.div>
            </header>

            {/* Main Chat Area */}
            <main ref={scrollRef} className="flex-1 overflow-y-auto px-4 md:px-8 py-6 pb-32 space-y-6 flex flex-col scroll-smooth z-10 custom-scrollbar">
                
                {/* Observability Dashboard pinned at the top inner scroll limit */}
                <div className="flex-shrink-0 px-2 pb-6">
                    <MetricsDashboard />
                </div>

                {/* Welcome State */}
                {messages.length === 0 && (
                    <motion.div 
                        initial={{ scale: 0.95, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ duration: 0.5, ease: "easeOut" }}
                        className="flex flex-col items-center justify-center h-full text-zinc-400 gap-6 mt-16"
                    >
                        <div className="relative group cursor-default">
                            <div className="absolute -inset-4 bg-gradient-to-r from-blue-600 to-violet-600 rounded-full blur-xl opacity-20 group-hover:opacity-40 transition duration-1000 group-hover:duration-200 animate-pulse"></div>
                            <div className="relative w-24 h-24 rounded-3xl glass-panel flex items-center justify-center shadow-2xl border border-white/10 overflow-hidden">
                                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-violet-500/10"></div>
                                <Bot size={40} className="text-blue-400 drop-shadow-[0_0_15px_rgba(96,165,250,0.5)]" />
                            </div>
                        </div>
                        <div className="text-center space-y-2">
                            <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-zinc-500">How can I help you today?</h2>
                            <p className="text-sm text-zinc-500 max-w-md mx-auto leading-relaxed">Agentic AI processes live tasks, conducts research, and writes production-ready code autonomously.</p>
                        </div>
                    </motion.div>
                )}

                {/* Message Mapping */}
                {messages.map((msg) => (
                    <MessageBubble key={msg.id} message={msg} />
                ))}

                {/* Processing Indicator */}
                {isProcessing && (
                    <div className="py-2">
                        <AgentSteps isProcessing={isProcessing} />
                    </div>
                )}

                {/* Invisible padding anchor point for scroll */}
                <div className="h-10 border-none" />
            </main>

            {/* Input Area */}
            <footer className="absolute bottom-0 w-full p-4 md:p-8 bg-gradient-to-t from-[#030303] via-[#030303]/80 to-transparent pt-24 z-20 pointer-events-none">
                <div className="pointer-events-auto">
                    <QueryInput onSend={handleSend} disabled={isProcessing} />
                    <p className="text-center text-xs font-medium text-zinc-600 mt-4 tracking-wide h-4">
                        Agentic AI processes live tasks accurately using LangGraph.
                    </p>
                </div>
            </footer>
        </div>
    );
}
