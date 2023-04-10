import redis

from config import settings
from utils import Singleton


class RedisClient(metaclass=Singleton):
    def __init__(self):
        self.pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

    @property
    def conn(self):
        if not hasattr(self, "_conn"):
            self.getConnection()
        return self._conn

    def getConnection(self):
        self._conn = redis.Redis(connection_pool=self.pool)