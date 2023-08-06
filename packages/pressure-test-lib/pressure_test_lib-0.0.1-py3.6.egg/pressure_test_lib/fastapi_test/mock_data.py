import json

from pressure_test_lib.base.constants import PressureTestRedisConfig, PressureTestConfig
from pressure_test_lib.cache.cache import local_cache

try:
    from aioredis import create_redis_pool
except:
    raise Exception('未安装 aioredis 库，支持 1.X.X 版本')


async def get_redis_connection():
    """获取一个redis连接"""
    if PressureTestRedisConfig.conn:
        return PressureTestRedisConfig.conn

    PressureTestRedisConfig.conn = await create_redis_pool(
        address=[PressureTestRedisConfig.host, PressureTestRedisConfig.port],
        db=PressureTestRedisConfig.db,
        password=PressureTestRedisConfig.password,
        minsize=PressureTestRedisConfig.minsize,
        maxsize=PressureTestRedisConfig.maxsize,
        timeout=PressureTestRedisConfig.timeout,
        encoding='utf-8',
        **(PressureTestRedisConfig.kwargs or {})
    )

    return PressureTestRedisConfig.conn


async def get_redis_mock_data_config():
    """获取redis里的mock数据"""
    conn = await get_redis_connection()
    mock_data_config = await conn.hgetall(PressureTestRedisConfig.mock_data_redis_key)
    return mock_data_config


async def init_cache_mock_data():
    """初始化mock_data的数据进内存"""
    if not PressureTestConfig.switch:
        # 如果不是压测命名空间，就不初始化mock数据
        return None
    redis_mock_data_config = await get_redis_mock_data_config()
    await local_cache.set(PressureTestConfig.mock_cache_key, redis_mock_data_config, PressureTestConfig.mock_cache_ex)
    return await local_cache.get(PressureTestConfig.mock_cache_key)
