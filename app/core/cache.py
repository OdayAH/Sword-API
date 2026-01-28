from functools import wraps
from typing import Any, Callable, Dict, List, Set
import json
import hashlib

class CacheManager:
    """In-memory cache manager with tag-based invalidation"""
    
    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.tags: Dict[str, Set[str]] = {}  # Maps tags to cache keys
    
    def get(self, key: str) -> Any:
        """Get value from cache"""
        return self.cache.get(key)
    
    def set(self, key: str, value: Any, tags: List[str] | None = None) -> None:
        """Set value in cache with optional tags"""
        self.cache[key] = value
        
        if tags:
            for tag in tags:
                if tag not in self.tags:
                    self.tags[tag] = set()
                self.tags[tag].add(key)
    
    def invalidate_tag(self, tag: str) -> None:
        """Invalidate all cache entries with a specific tag"""
        if tag in self.tags:
            for key in self.tags[tag]:
                self.cache.pop(key, None)
            self.tags[tag].clear()
    
    def invalidate_tags(self, tags: List[str]) -> None:
        """Invalidate all cache entries with any of the specified tags"""
        for tag in tags:
            self.invalidate_tag(tag)
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
        self.tags.clear()


# Global cache instance
cache_manager = CacheManager()


def generate_cache_key(prefix: str, **kwargs) -> str:
    """Generate a cache key from prefix and kwargs"""
    params = json.dumps(kwargs, sort_keys=True, default=str)
    hash_suffix = hashlib.md5(params.encode()).hexdigest()[:8]
    return f"{prefix}:{hash_suffix}"


def cached(prefix: str, tags: List[str] | None = None):
    """
    Decorator to cache function results with tag-based invalidation
    
    Args:
        prefix: Cache key prefix
        tags: List of tags to associate with cached result
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            cache_key = generate_cache_key(prefix, args=args, kwargs=kwargs)
            
            # Try to get from cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call the actual function
            result = func(*args, **kwargs)
            
            # Store in cache with tags
            cache_manager.set(cache_key, result, tags=tags)
            
            return result
        
        return wrapper
    return decorator
