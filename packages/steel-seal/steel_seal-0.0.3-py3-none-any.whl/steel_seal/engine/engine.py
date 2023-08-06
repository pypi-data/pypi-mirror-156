from abc import ABC


class Engine(ABC):
    def add(self, key: str):
        """
        添加Key到记录列表
        :param key: 唯一标识符
        :return:
        """

    def exist(self, key: str) -> bool:
        """
        判断当前Key是否已存在
        :param key: 唯一标识符
        :return:
        """