import threading
from typing import Dict, Any

class MetricsCollector:
    """
    In-memory metrics collector recording platform observability metrics.
    """
    def __init__(self):
        self.lock = threading.Lock()
        self.total_requests = 0
        self.total_cache_hits = 0
        self.total_rag_used = 0
        self.total_latency_ms = 0.0
        self.total_iterations = 0
        self.total_classifier_time = 0.0
        self.total_code_generator_time = 0.0
        self.total_code_reviewer_time = 0.0

    def record_request(self, metrics: Dict[str, Any]):
        """
        Record a single request's execution parameters.
        Expects keys: latency_ms, cache_hit, rag_used, iterations
        """
        with self.lock:
            self.total_requests += 1
            
            if metrics.get("cache_hit"):
                self.total_cache_hits += 1
                
            if metrics.get("rag_used"):
                self.total_rag_used += 1
                
            self.total_latency_ms += float(metrics.get("latency_ms", 0))
            self.total_iterations += int(metrics.get("iterations", 1))

            self.total_classifier_time += float(metrics.get("classifier_time", 0))
            self.total_code_generator_time += float(metrics.get("code_generator_time", 0))
            self.total_code_reviewer_time += float(metrics.get("code_reviewer_time", 0))

    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Returns an aggregated summary of all requests.
        """
        with self.lock:
            total = self.total_requests
            
            if total == 0:
                return {
                    "total_requests": 0,
                    "cache_hit_rate": 0.0,
                    "rag_usage_rate": 0.0,
                    "avg_latency_ms": 0.0,
                    "avg_iterations": 0.0
                }
                
            return {
                "total_requests": total,
                "cache_hit_rate": round(self.total_cache_hits / total, 4),
                "rag_usage_rate": round(self.total_rag_used / total, 4),
                "avg_latency_ms": round(self.total_latency_ms / total, 2),
                "avg_iterations": round(self.total_iterations / total, 2),
                "avg_classifier_time": round(self.total_classifier_time / total, 2),
                "avg_code_generator_time": round(self.total_code_generator_time / total, 2),
                "avg_code_reviewer_time": round(self.total_code_reviewer_time / total, 2)
            }
