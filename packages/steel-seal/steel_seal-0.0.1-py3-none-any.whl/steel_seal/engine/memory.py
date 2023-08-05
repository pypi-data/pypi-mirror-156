import time
from pydantic import BaseModel
from typing import List
from .engine import Engine


# 初始化参数
class MemoryOptions(BaseModel):
    # 指定缓存过期时间，单位：秒
    # 默认300秒后历史记录自动过期
    expire_time = 3


# 缓存的数据单元
class CacheUint(BaseModel):
    key: str
    time: int


class MemoryEngine(Engine):
    def __init__(self, *args: MemoryOptions):
        # 用于缓存记录的队列
        self.__list: List[CacheUint] = []
        # 用于查询缓存记录的词典
        self.__dict: dict[str, bool] = {}
        # 最少20秒回收一次过期缓存
        self.__recycling_time = 20
        # 上次执行回收任务时间
        self._last_recycling_time = int(time.time())
        # 初始化配置参数
        # 如果没有指定配置参数则默认记录300秒后自动过期
        self.__options = args[0] if len(args) > 0 else MemoryOptions()

    def add(self, key: str):
        """
        添加记录到缓存列表
        :param key:
        :return:
        """
        if self.__dict.__contains__(key):
            return

        cur_time = int(time.time())

        if cur_time - self._last_recycling_time > self.__recycling_time:
            self.__recycling_cache()

        self.__list.append(CacheUint(
            key=key,
            time=cur_time
        ))
        self.__dict[key] = True

    def exist(self, key: str) -> bool:
        """
        判断记录是否已存在
        :param key:
        :return:
        """
        return self.__dict.__contains__(key)

    def __recycling_cache(self):
        """对过期记录进行释放"""
        cur_time = int(time.time())

        for i in range(len(self.__list)):
            cache = self.__list[i]

            if cache.time + self.__options.expire_time < cur_time and self.__dict.__contains__(cache.key):
                del self.__dict[cache.key]
                continue

            self.__list = self.__list[i:]
