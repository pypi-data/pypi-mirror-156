import time


class LocalCache:
    """
    本地缓存
    """

    def __init__(self):
        self._cache = {}

    def set(self, key, value, expire=0):
        """设置缓存
        expire： -1为不会过期，>=0是过期时间，单位秒
        """
        self._cache.update({
            key: {
                "data": value,
                "expire": self._get_expired_time(expire)
            }
        })

    def get(self, key):
        result = self._cache.get(key)
        if result:
            return result
        return None

    @staticmethod
    def is_expired(result: dict):
        """是否过期"""
        if result.get("expire", 0) > int(time.time()):
            return False
        return True

    @staticmethod
    def _get_expired_time(expire: int):
        """获取合法过期时间"""
        return int(time.time()) + expire if expire >= 0 else int(time.time())


local_cache = LocalCache()
