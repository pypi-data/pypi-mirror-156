"""常量"""


class PressureTestConfig:
    """压测配置"""

    # 开关
    switch = 0

    # 压测mock数据内存key
    mock_cache_key = 'mock_cache_key'

    # 内存过期时间
    mock_cache_ex = 60

    # 服务名称
    service_name = ''


class PressureTestRedisConfig:
    """压测redis配置"""
    # 压测所属服务
    service = 'default'

    # 地址
    host = '127.0.0.1'

    # 端口
    port = 6379

    # 数据库
    db = 0

    # 密码
    password = None

    # 最小连接数
    minsize = 1

    # 最大连接数
    maxsize = 10

    # 超时时间【毫秒】
    timeout = 5000

    # 额外参数
    kwargs = None

    # 初始化连接池
    conn = None

    # mock数据的redis_key
    mock_data_redis_key = 'mock_data'
