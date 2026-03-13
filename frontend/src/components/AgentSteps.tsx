"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";

const STAGES = [
    "Planner",
    "Knowledge Retrieval",
    "Research",
    "Writer",
    "Critic"
];

export function AgentSteps({ isProcessing }: { isProcessing: boolean }) {
    const [activeStage, setActiveStage] = useState(0);

    // Fake a progression ticker to simulate the graph pipeline since API is synchronous POST
    useEffect(() => {
        let interval: NodeJS.Timeout;
        if (isProcessing) {
            setActiveStage(0);
            interval = setInterval(() => {
                setActiveStage((prev) => {
                    if (prev >= STAGES.length - 1) return prev;
                    return prev + 1;
                });
            }, 3000); // Progress every 3 seconds to keep UI active
        } else {
            setActiveStage(STAGES.length); // Mark all as completed when done processing
        }

        return () => clearInterval(interval);
    }, [isProcessing]);

    if (!isProcessing) return null;

    return (
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 w-full max-w-sm mx-auto shadow-2xl space-y-4">
            <h3 className="text-zinc-100 font-medium pb-2 border-b border-zinc-800">
                Agentic Workflow
            </h3>
            <div className="flex flex-col gap-3">
                {STAGES.map((stage, index) => {
                    const isCompleted = index < activeStage;
                    const isCurrent = index === activeStage;
                    const isPending = index > activeStage;

                    return (
                        <motion.div
                            key={stage}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className={`flex items-center gap-3 text-sm font-medium ${isCompleted ? "text-emerald-500" :
                                    isCurrent ? "text-blue-400" : "text-zinc-600"
                                }`}
                        >
                            {isCompleted ? (
                                <CheckCircle2 size={18} />
                            ) : isCurrent ? (
                                <Loader2 size={18} className="animate-spin" />
                            ) : (
                                <Circle size={18} />
                            )}
                            {stage}
                        </motion.div>
                    );
                })}
            </div>
        </div>
    );
}
