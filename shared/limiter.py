import os
from redis import Redis
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


# Parse Redis URL from env
storage_uri = os.getenv("REDIS_URL")


limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=storage_uri,
)
