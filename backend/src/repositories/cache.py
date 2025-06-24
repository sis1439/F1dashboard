import redis
import json
import pickle
from typing import Any, Optional, Union
from datetime import datetime, timedelta
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class CacheRepository:
    """Cache repository for managing Redis cache operations"""
    
    def __init__(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            # Fallback to a mock cache for development
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache by key"""
        try:
            if not self.redis_client:
                return None
                
            cached_data = self.redis_client.get(key)
            if cached_data:
                try:
                    # Try JSON first
                    return json.loads(cached_data)
                except json.JSONDecodeError:
                    # Fallback to pickle for complex objects
                    return pickle.loads(cached_data.encode('latin1'))
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL (time to live) in seconds"""
        try:
            if not self.redis_client:
                return False
                
            try:
                # Try JSON serialization first
                serialized_value = json.dumps(value)
            except TypeError:
                # Fallback to pickle for complex objects
                serialized_value = pickle.dumps(value).decode('latin1')
            
            self.redis_client.setex(key, ttl, serialized_value)
            logger.debug(f"Cached data for key {key} with TTL {ttl}")
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache by key"""
        try:
            if not self.redis_client:
                return False
                
            result = self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            if not self.redis_client:
                return 0
                
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error for pattern {pattern}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            if not self.redis_client:
                return False
                
            return self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists check error for key {key}: {e}")
            return False
    
    def get_ttl(self, key: str) -> int:
        """Get TTL for key in seconds (-1 if no expiry, -2 if key doesn't exist)"""
        try:
            if not self.redis_client:
                return -2
                
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Cache TTL check error for key {key}: {e}")
            return -2
    
    def keys(self, pattern: str = "*") -> list:
        """Get all keys matching pattern"""
        try:
            if not self.redis_client:
                return []
                
            return self.redis_client.keys(pattern)
        except Exception as e:
            logger.error(f"Cache keys error for pattern {pattern}: {e}")
            return []
    
    def flush_all(self) -> bool:
        """Clear all cache"""
        try:
            if not self.redis_client:
                return False
                
            self.redis_client.flushdb()
            logger.info("Cache flushed successfully")
            return True
        except Exception as e:
            logger.error(f"Cache flush error: {e}")
            return False
    
    def get_cache_info(self, key: str) -> dict:
        """Get cache information for a key"""
        try:
            if not self.exists(key):
                return {"cached": False}
            
            ttl = self.get_ttl(key)
            expires_at = None
            if ttl > 0:
                expires_at = datetime.now() + timedelta(seconds=ttl)
            
            return {
                "cached": True,
                "cache_key": key,
                "cached_at": datetime.now(),  # Approximation
                "expires_at": expires_at
            }
        except Exception as e:
            logger.error(f"Cache info error for key {key}: {e}")
            return {"cached": False}


# Global cache repository instance
cache_repo = CacheRepository() 