from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend
from app.src.core.config import config

backend_result = RedisAsyncResultBackend(redis_url=config.redis.url)

broker = AioPikaBroker(
    url=config.broker.url,
    exchange_name="taskiq_exchange",
    queue_name="taskiq_queue",
    qos=5,
).with_result_backend(backend_result)
