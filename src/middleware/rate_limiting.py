"""
Rate limiting and caching middleware
"""
import time
from functools import wraps
from typing import Dict, Any
from flask import request, jsonify
import hashlib
import json


class RateLimiter:
    def __init__(self):
        self.clients = {}  # In production, use Redis
        self.cache = {}    # In production, use Redis
    
    def is_rate_limited(self, client_ip: str, limit: int = 10, window: int = 60) -> bool:
        """Check if client is rate limited"""
        current_time = time.time()
        client_key = f"rate_limit:{client_ip}"
        
        if client_key not in self.clients:
            self.clients[client_key] = []
        
        # Remove old timestamps
        self.clients[client_key] = [
            timestamp for timestamp in self.clients[client_key]
            if current_time - timestamp < window
        ]
        
        # Check if limit exceeded
        if len(self.clients[client_key]) >= limit:
            return True
        
        # Add current request
        self.clients[client_key].append(current_time)
        return False
    
    def get_cache_key(self, data: Dict[str, Any]) -> str:
        """Generate cache key from request data"""
        # Sort keys for consistent hashing
        sorted_data = json.dumps(data, sort_keys=True)
        return hashlib.md5(sorted_data.encode()).hexdigest()
    
    def get_cached_result(self, cache_key: str, ttl: int = 300):
        """Get cached result if not expired"""
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < ttl:
                return cached_data
        return None
    
    def cache_result(self, cache_key: str, result: Any):
        """Cache the result with timestamp"""
        self.cache[cache_key] = (result, time.time())


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(limit: int = 10, window: int = 60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            
            if rate_limiter.is_rate_limited(client_ip, limit, window):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'limit': limit,
                    'window': window
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def cache_response(ttl: int = 300):
    """Response caching decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Only cache GET requests with JSON responses
            if request.method != 'GET':
                return f(*args, **kwargs)
            
            cache_key = rate_limiter.get_cache_key({
                'url': request.url,
                'args': request.args.to_dict()
            })
            
            cached_result = rate_limiter.get_cached_result(cache_key, ttl)
            if cached_result:
                return cached_result
            
            result = f(*args, **kwargs)
            rate_limiter.cache_result(cache_key, result)
            
            return result
        return decorated_function
    return decorator
