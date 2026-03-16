from config.settings import settings

class RedisCache:
    """
    Handles caching of agent responses using Redis.
    """
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        # Initialize Redis client using centralized settings
        redis_url = settings.REDIS_URL
        if redis_url:
            self.client = redis.from_url(redis_url, decode_responses=True)
        else:
            self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        
    def _generate_key(self, query: str) -> str:
        """
        Generates a consistent deterministic cache key based on the user task.
        Normalizes the query space by stripping and lowercasing.
        """
        normalized_query = query.lower().strip()
        query_hash = hashlib.md5(normalized_query.encode("utf-8")).hexdigest()
        return f"agent_cache:{query_hash}"

    def get_cached_answer(self, query: str) -> Optional[dict]:
        """
        Retrieves a cached answer for the given query if it exists.
        Returns the parsed dictionary or None.
        """
        try:
            key = self._generate_key(query)
            cached_data = self.client.get(key)
            if cached_data:
                print(f"[RedisCache] Cache HIT for query: '{query}'")
                return json.loads(cached_data)
            
            print(f"[RedisCache] Cache MISS for query: '{query}'")
            return None
        except Exception as e:
            print(f"[RedisCache] Error retrieving from cache: {str(e)}")
            return None

    def set_cached_answer(self, query: str, answer: dict, expire_seconds: int = 3600):
        """
        Saves the generated answer dict to Redis, defaulting to a 1 hour expiration.
        """
        try:
            key = self._generate_key(query)
            # Serialize structured answer dict to JSON string for storage
            self.client.setex(key, expire_seconds, json.dumps(answer))
            print(f"[RedisCache] Cached answer stored successfully.")
        except Exception as e:
            print(f"[RedisCache] Error setting cache: {str(e)}")
