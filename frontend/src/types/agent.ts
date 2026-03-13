export interface ResearchFinding {
  step?: string;
  result?: string;
  title?: string;
  url?: string;
  snippet?: string;
}

export interface FinalResponse {
  task: string;
  summary: string;
  recommendations: Record<string, string>[];
}

export interface AgentWorkflowResponse {
  task: string;
  iterations_used: number;
  cache_hit: boolean;
  final_answer: FinalResponse;

  // Extra detailed context returned by phase 9 additions
  knowledge_used?: boolean;
  knowledge_chunks?: any[];
  web_search_results?: ResearchFinding[];

  // Extra detailed context returned by phase 15 code generation additions
  task_type?: "research" | "coding";
  generated_code?: string;
  improved_code?: string;
  review_feedback?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
  metadata?: AgentWorkflowResponse;
  error?: string;
}

export interface SystemMetrics {
  total_requests: number;
  cache_hit_rate: number;
  rag_usage_rate: number;
  avg_latency_ms: number;
  avg_iterations: number;
  avg_code_generator_time?: number;
  avg_code_reviewer_time?: number;
  avg_classifier_time?: number;
}
