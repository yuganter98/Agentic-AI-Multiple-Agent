"use client";

import { useEffect, useState } from "react";
import { SystemMetrics } from "../types/agent";
import { fetchMetrics } from "../services/api";
import { Activity, Zap, Server, Clock, RefreshCw } from "lucide-react";
import { motion } from "framer-motion";

export function MetricsDashboard() {
    const [metrics, setMetrics] = useState<SystemMetrics | null>(null);

    useEffect(() => {
        // Initial fetch
        let isMounted = true;

        const loadMetrics = async () => {
            try {
                const data = await fetchMetrics();
                if (isMounted) setMetrics(data);
            } catch (e) {
                console.error("Dashboard failed to fetch metrics", e);
            }
        };

        loadMetrics();

        // Poll every 5 seconds
        const intervalId = setInterval(loadMetrics, 5000);

        return () => {
            isMounted = false;
            clearInterval(intervalId);
        };
    }, []);

    if (!metrics) return null;

    return (
        <div className="w-full max-w-4xl mx-auto py-6">
            <div className="flex items-center justify-between mb-4 px-2">
                <h2 className="text-zinc-200 font-semibold tracking-wide flex items-center gap-2">
                    <Activity size={18} className="text-emerald-500" />
                    System Observability
                </h2>
                <span className="text-[10px] font-bold tracking-wide text-emerald-400 flex items-center gap-2 glass-pill px-3 py-1.5 rounded-full shadow-inner border-white/5 bg-zinc-900/40">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse drop-shadow-[0_0_5px_rgba(16,185,129,0.8)]"></span>
                    LIVE UPDATING
                </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {/* Total Requests */}
                <MetricCard
                    title="Total Requests"
                    value={metrics.total_requests}
                    icon={<Server size={16} />}
                    color="text-blue-400"
                />

                {/* Cache Hit Rate */}
                <MetricCard
                    title="Cache Hit Rate"
                    value={`${(metrics.cache_hit_rate * 100).toFixed(1)}%`}
                    icon={<Zap size={16} />}
                    color="text-amber-500"
                />

                {/* RAG Usage */}
                <MetricCard
                    title="RAG Usage"
                    value={`${(metrics.rag_usage_rate * 100).toFixed(1)}%`}
                    icon={<RefreshCw size={16} />}
                    color="text-indigo-400"
                />

                {/* Latency */}
                <MetricCard
                    title="Avg Latency"
                    value={`${Math.round(metrics.avg_latency_ms)} ms`}
                    icon={<Clock size={16} />}
                    color="text-rose-400"
                />

                {/* Iterations */}
                <MetricCard
                    title="Avg Iterations"
                    value={metrics.avg_iterations.toFixed(1)}
                    icon={<Activity size={16} />}
                    color="text-zinc-300"
                />

                {/* Optional Coding Metrics */}
                {metrics.avg_classifier_time !== undefined && metrics.avg_classifier_time > 0 && (
                    <MetricCard
                        title="Classifier Time"
                        value={`${Math.round(metrics.avg_classifier_time)} ms`}
                        icon={<Activity size={16} />}
                        color="text-pink-400"
                    />
                )}

                {metrics.avg_code_generator_time !== undefined && metrics.avg_code_generator_time > 0 && (
                    <MetricCard
                        title="Generator Time"
                        value={`${Math.round(metrics.avg_code_generator_time)} ms`}
                        icon={<Zap size={16} />}
                        color="text-fuchsia-400"
                    />
                )}

                {metrics.avg_code_reviewer_time !== undefined && metrics.avg_code_reviewer_time > 0 && (
                    <MetricCard
                        title="Reviewer Time"
                        value={`${Math.round(metrics.avg_code_reviewer_time)} ms`}
                        icon={<Clock size={16} />}
                        color="text-purple-400"
                    />
                )}
            </div>
        </div>
    );
}

function MetricCard({ title, value, icon, color }: { title: string, value: string | number, icon: React.ReactNode, color: string }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            key={value?.toString()} // Trigger subtle animation when value updates
            className="glass-card p-5 rounded-2xl flex flex-col items-center justify-center gap-3 relative overflow-hidden group shadow-lg hover:shadow-xl hover:border-white/10 transition-all duration-300 transform group-hover:-translate-y-1"
        >
            <div className={`flex items-center gap-2 text-[11px] font-bold text-zinc-400 uppercase tracking-widest z-10 drop-shadow-sm`}>
                <span className={color.replace("text-", "text-").concat(" drop-shadow-[0_0_5px_currentColor]")}>{icon}</span>
                <span className="truncate">{title}</span>
            </div>
            <div className="text-2xl md:text-3xl font-extrabold tracking-tighter text-zinc-100 z-10 drop-shadow-md">
                {value}
            </div>

            {/* Background glow decoration */}
            <div className={`absolute -bottom-8 -right-8 w-28 h-28 ${color.replace('text-', 'bg-')}/10 rounded-full blur-2xl group-hover:scale-150 transition-transform duration-700 ease-out`}></div>
        </motion.div>
    );
}
