import os
import sys

def get_redis_values():
    # look for .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    host = os.environ.get("REDIS_URL", "redis://localhost")
    password = os.environ.get("REDIS_PASSWORD", None)
    port = os.environ.get("REDIS_PORT", 6379)
    username = os.environ.get("REDIS_USERNAME", None)
    redis_url = f"redis://{username}:{password}@{host}:{port}"
    return redis_url