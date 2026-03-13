"use client";
import { useState, FormEvent, useRef, KeyboardEvent } from "react";
import { Send, Sparkles } from "lucide-react";
import { LoadingSpinner } from "./LoadingSpinner";
import TextareaAutosize from "react-textarea-autosize";

interface QueryInputProps {
    onSend: (message: string) => void;
    disabled: boolean;
}

export function QueryInput({ onSend, disabled }: QueryInputProps) {
    const [query, setQuery] = useState("");
    const formRef = useRef<HTMLFormElement>(null);

    const handleSubmit = (e?: FormEvent) => {
        if (e) e.preventDefault();
        if (query.trim() && !disabled) {
            onSend(query);
            setQuery("");
        }
    };

    const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    return (
        <form
            ref={formRef}
            onSubmit={handleSubmit}
            className="relative flex items-end w-full max-w-4xl mx-auto rounded-3xl glass-panel focus-within:ring-2 focus-within:ring-blue-500/50 focus-within:border-blue-400/50 transition-all p-2 pr-3"
        >
            <div className="pl-4 pr-3 pb-3 text-blue-400">
                <Sparkles size={22} className="drop-shadow-[0_0_8px_rgba(96,165,250,0.5)]" />
            </div>
            
            <TextareaAutosize
                minRows={1}
                maxRows={6}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={disabled}
                placeholder="Message Agentic AI... (Shift+Enter for newline)"
                className="flex-1 bg-transparent text-zinc-100 placeholder:text-zinc-500 py-3.5 outline-none disabled:opacity-50 resize-none font-medium text-[15px] leading-relaxed custom-scrollbar"
            />
            
            <div className="pl-2 pb-1.5">
                <button
                    type="submit"
                    disabled={disabled || !query.trim()}
                    className="flex items-center justify-center h-10 w-10 rounded-full bg-blue-600 text-white hover:bg-blue-500 hover:scale-105 active:scale-95 disabled:bg-zinc-800 disabled:text-zinc-600 disabled:hover:scale-100 transition-all shadow-md"
                >
                    {disabled ? <LoadingSpinner size={18} /> : <Send size={18} className="translate-x-[1px]" />}
                </button>
            </div>
        </form>
    );
}
