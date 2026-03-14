import { AgentWorkflowResponse } from "../types/agent";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function submitTask(task: string): Promise<AgentWorkflowResponse> {
    const response = await fetch(`${API_BASE_URL}/task`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ task }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to process task");
    }

    const data: AgentWorkflowResponse = await response.json();
    return data;
}

export async function fetchMetrics(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/metrics`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        },
        // Prevent caching to ensure realtime updates
        cache: "no-store",
    });

    if (!response.ok) {
        throw new Error("Failed to fetch system metrics");
    }

    return await response.json();
}
