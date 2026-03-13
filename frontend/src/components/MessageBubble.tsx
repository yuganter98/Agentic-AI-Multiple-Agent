"use client";
import { ChatMessage } from "../types/agent";
import { motion } from "framer-motion";
import { Bot, User, Zap, RefreshCw, FileText, Globe } from "lucide-react";
import { cn } from "../lib/utils";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

export function MessageBubble({ message }: { message: ChatMessage }) {
    const isAI = message.role === "assistant";

    return (
        <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            className={cn(
                "flex w-full gap-5 max-w-4xl mx-auto py-6 group",
                isAI ? "justify-start" : "justify-end"
            )}
        >
            {/* AI Avatar */}
            {isAI && (
                <div className="flex-shrink-0 w-11 h-11 rounded-2xl glass-panel flex items-center justify-center border border-blue-500/30 text-blue-400 shadow-[0_0_15px_rgba(37,99,235,0.15)] relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-indigo-500/10"></div>
                    <Bot size={22} className="drop-shadow-md z-10" />
                </div>
            )}

            {/* Bubble Box */}
            <div
                className={cn(
                    "flex flex-col max-w-[85%] rounded-3xl px-6 py-5",
                    isAI
                        ? "glass-panel text-zinc-300 rounded-tl-sm shadow-xl"
                        : "bg-gradient-to-br from-blue-600 to-indigo-700 text-white rounded-tr-sm shadow-lg border border-white/10"
                )}
            >
                {/* User Raw Content */}
                {!message.metadata && (
                    <div className="text-[15px] whitespace-pre-wrap leading-relaxed font-medium">
                        {message.content}
                    </div>
                )}

                {/* AI Structured Content */}
                {message.metadata && (
                    <div className="flex flex-col gap-6">
                        {/* Metadata Header */}
                        <div className="flex items-center gap-4 text-[11px] font-semibold px-3.5 py-2 glass-pill rounded-full w-fit tracking-wide shadow-inner">
                            {message.metadata.cache_hit ? (
                                <span className="flex items-center gap-1.5 text-amber-500 drop-shadow-[0_0_5px_rgba(245,158,11,0.5)]">
                                    <Zap size={14} /> CACHED
                                </span>
                            ) : (
                                <span className="flex items-center gap-1.5 text-blue-400 drop-shadow-[0_0_5px_rgba(96,165,250,0.5)]">
                                    <RefreshCw size={14} /> LIVE COMPUTED
                                </span>
                            )}
                            <span className="text-zinc-700">|</span>
                            <span className="text-zinc-400">
                                ITERATIONS: <span className="text-zinc-200">{message.metadata.iterations_used}</span>
                            </span>
                        </div>

                        {/* Answer Summary */}
                        <div className="text-[15px] leading-relaxed text-zinc-100 font-medium tracking-wide">
                            {message.metadata.final_answer.summary}
                        </div>

                        {/* Generated Code Display */}
                        {message.metadata.task_type === "coding" && (message.metadata.improved_code || message.metadata.generated_code) && (
                            <div className="my-2 rounded-xl border border-zinc-800/80 bg-[#1e1e1e] overflow-hidden shadow-2xl relative">
                                <div className="flex items-center justify-between px-4 py-3 bg-[#2d2d2d] border-b border-black">
                                    {/* macOS Style Controls */}
                                    <div className="flex items-center gap-2">
                                        <div className="w-3 h-3 rounded-full bg-red-500/80 shadow-inner"></div>
                                        <div className="w-3 h-3 rounded-full bg-yellow-500/80 shadow-inner"></div>
                                        <div className="w-3 h-3 rounded-full bg-emerald-500/80 shadow-inner"></div>
                                    </div>
                                    
                                    <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400 pr-2">
                                        <Bot size={14} /> 
                                        {message.metadata.improved_code && message.metadata.review_feedback !== "Looks good." ? "Reviewed & Validated Code" : "Generated Code"}
                                    </div>
                                </div>

                                {message.metadata.review_feedback && message.metadata.review_feedback !== "Looks good." && (
                                    <div className="px-4 py-2 bg-amber-950/30 border-b border-amber-900/30 text-xs text-amber-400 font-mono">
                                        ⚠️ Reviewer Insights: {message.metadata.review_feedback}
                                    </div>
                                )}
                                
                                <div className="max-w-full overflow-x-auto custom-scrollbar">
                                    <SyntaxHighlighter 
                                        language="python" 
                                        style={vscDarkPlus} 
                                        customStyle={{ margin: 0, padding: '1.25rem', fontSize: '14px', background: 'transparent' }}
                                        wrapLongLines={false}
                                    >
                                        {message.metadata.improved_code || message.metadata.generated_code || ""}
                                    </SyntaxHighlighter>
                                </div>
                            </div>
                        )}

                        {/* Recommendations */}
                        {message.metadata.final_answer.recommendations?.length > 0 && (
                            <div className="space-y-3">
                                <h4 className="text-xs font-bold text-zinc-500 uppercase tracking-widest pl-1">
                                    Recommendations
                                </h4>
                                <div className="grid gap-3">
                                    {message.metadata.final_answer.recommendations.map((rec: any, i: number) => (
                                        <div key={i} className="glass-card p-4 rounded-xl border border-white/5 text-sm transition-transform hover:-translate-y-0.5">
                                            {Object.entries(rec).map(([k, v]) => (
                                                <div key={k} className="flex flex-col md:flex-row md:items-start md:gap-3 py-1.5 border-b border-zinc-800/50 last:border-0 text-zinc-200">
                                                    <span className="font-semibold text-zinc-400 min-w-[100px] capitalize text-xs tracking-wider">{k.replace(/_/g, ' ')}</span>
                                                    <span className="flex-1 whitespace-pre-wrap font-medium">
                                                        {typeof v === 'object' && v !== null ? JSON.stringify(v, null, 2) : String(v)}
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Attached Sources */}
                        <SourcesView
                            knowledgeChunks={message.metadata.knowledge_chunks}
                            webSearch={message.metadata.web_search_results}
                        />
                    </div>
                )}

                {/* Error State */}
                {message.error && (
                    <div className="text-red-400 text-sm p-4 bg-red-950/40 backdrop-blur-md border border-red-900/60 rounded-xl font-medium shadow-md">
                        ⚠️ Processing Failed: {message.error}
                    </div>
                )}
            </div>

            {/* User Avatar */}
            {!isAI && (
                <div className="flex-shrink-0 w-11 h-11 rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-lg border border-white/10 ring-2 ring-blue-500/20">
                    <User size={22} className="drop-shadow-md" />
                </div>
            )}
        </motion.div>
    );
}

function SourcesView({ knowledgeChunks, webSearch }: { knowledgeChunks?: any[], webSearch?: any[] }) {
    if (!knowledgeChunks?.length && !webSearch?.length) return null;

    return (
        <div className="mt-4 pt-5 border-t border-zinc-800/60 space-y-4">
            <h4 className="text-[11px] font-bold text-zinc-500 uppercase tracking-widest pl-1">
                Sources Consulted
            </h4>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {/* Knowledge Base Sources */}
                {knowledgeChunks && knowledgeChunks.length > 0 && knowledgeChunks.slice(0, 3).map((chunk, i) => (
                    <div key={`k-${i}`} className="flex items-start gap-3 glass-card p-3.5 rounded-xl border border-white/5 text-xs text-zinc-300 transition-transform hover:-translate-y-1 hover:shadow-lg hover:shadow-emerald-500/5 group/card cursor-default">
                        <FileText size={16} className="text-emerald-500 mt-0.5 flex-shrink-0 group-hover/card:text-emerald-400 transition-colors drop-shadow-[0_0_5px_rgba(16,185,129,0.3)]" />
                        <div className="line-clamp-3 leading-relaxed font-medium">
                            {typeof chunk === 'string' ? chunk : JSON.stringify(chunk)}
                        </div>
                    </div>
                ))}

                {/* Web Search Sources */}
                {webSearch && webSearch.length > 0 && webSearch.slice(0, 3).map((res: any, i) => (
                    <div key={`w-${i}`} className="flex flex-col gap-1.5 glass-card p-3.5 rounded-xl border border-white/5 text-xs text-zinc-400 transition-transform hover:-translate-y-1 hover:shadow-lg hover:shadow-blue-500/5 group/card cursor-default">
                        <span className="flex items-center gap-2 font-bold text-blue-400 truncate group-hover/card:text-blue-300 transition-colors drop-shadow-[0_0_5px_rgba(96,165,250,0.3)]">
                            <Globe size={14} className="flex-shrink-0" /> {res.result || res.title || 'Unknown Web Source'}
                        </span>
                        {(res.snippet) && <span className="line-clamp-2 leading-relaxed font-medium mt-1">{res.snippet}</span>}
                    </div>
                ))}
            </div>
        </div>
    );
}
