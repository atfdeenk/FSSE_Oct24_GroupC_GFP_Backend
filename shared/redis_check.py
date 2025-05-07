import os
import redis


def check_redis_connection(app):
    """Optional Redis connection check during app startup (for logging)."""
    if app.testing:
        return  # Skip in testing mode

    try:
        redis_url = app.config.get("REDIS_URL") or os.getenv("REDIS_URL")
        redis_client = redis.Redis.from_url(redis_url)
        redis_client.ping()
        app.logger.info("✅ Redis limiter storage connected successfully.")
    except Exception as e:
        app.logger.error(f"❌ Failed to connect to Redis Limiter: {e}")
