import json
import redis

from pressure_test_lib.base.constants import PressureTestRedisConfig, PressureTestConfig
from pressure_test_lib.cache.cache import local_cache


def get_redis_connection():
    """获取一个redis连接"""
    if PressureTestRedisConfig.conn is None:
        connection_pool = redis.ConnectionPool(
            host=PressureTestRedisConfig.host,
            port=PressureTestRedisConfig.port,
            password=PressureTestRedisConfig.password,
            db=PressureTestRedisConfig.db,
            socket_timeout=PressureTestRedisConfig.timeout,
            max_connections=PressureTestRedisConfig.maxsize,
            decode_responses=True
        )
        PressureTestRedisConfig.conn = redis.Redis(connection_pool=connection_pool)

    return PressureTestRedisConfig.conn


def get_redis_mock_data_config():
    """获取redis里的mock数据"""
    conn = get_redis_connection()
    mock_data_config = conn.hgetall(PressureTestRedisConfig.mock_data_redis_key)
    return mock_data_config


def init_cache_mock_data():
    """初始化mock_data的数据进内存"""
    if not PressureTestConfig.switch:
        # 如果不是压测命名空间，就不初始化mock数据
        return None
    redis_mock_data_config = get_redis_mock_data_config()
    local_cache.set(PressureTestConfig.mock_cache_key, redis_mock_data_config, PressureTestConfig.mock_cache_ex)
    return local_cache.get(PressureTestConfig.mock_cache_key)
