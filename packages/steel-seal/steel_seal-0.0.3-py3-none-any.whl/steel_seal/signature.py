import hashlib
import time

from pydantic import BaseModel
from .engine import Engine, MemoryEngine
from .util import get_random_str


class Signature(BaseModel):
    # 当前用于签名的时间戳
    timestamp: int
    # 用于签名的随机内容
    nonce: str
    # 返回签名内容
    signature: str


class SteelSeal:
    """
    SteelSeal Class

    参数：
        token： 必填，用于签名或验签的令牌
        engine： 选填，指定当前实例使用的存储引擎，主要用于防重放。如果不指定，则默认使用MemoryEngine
    """
    def __init__(self, token: str, *args: Engine):
        """初始化签名实例"""
        self.__token = token
        self.__engine = args[0] if len(args) > 0 else MemoryEngine()

    @staticmethod
    def generate_token() -> str:
        """
        生成一个新的Token
        :return: 返回生成的Token
        """
        return get_random_str(32)

    def signature(self, data: str) -> Signature:
        """
        对数据进行签名
        :param data: 需要进行签名的数据
        :return: 签名对象，主要包括timestamp,nonce,signature
        """
        nonce = get_random_str(8)
        timestamp = int(time.time())

        signature = self.__sort_and_hash(self.__token, data, nonce, str(timestamp))
        return Signature(
            timestamp=timestamp,
            nonce=nonce,
            signature=signature
        )

    def verify(self, data: str, sig_info: Signature) -> bool:
        """
        使用token对签名进行验证
        :param data: 用于进行验签的数据，一般是指query或者body参数
        :param sig_info: 从请求的Query中获取的签名对象，主要包括timestamp、nonce、signature
        :return: 签名是否合法
        """
        cur_time = int(time.time())

        # 如果签名时间超过5分钟则判定当前签名已过期
        if sig_info.timestamp and cur_time - sig_info.timestamp > 300:
            return False

        # 如过缓存中存在当前签名记录则判定签名已被使用
        if self.__engine:
            if self.__engine.exist(sig_info.nonce):
                return False
            self.__engine.add(sig_info.nonce)

        return self.__sort_and_hash(self.__token, data, sig_info.nonce, str(sig_info.timestamp)) == sig_info.signature

    def __sort_and_hash(self, *args) -> str:
        """
        对参数进行字典排序并计算Hash
        :param args:
        :return:
        """
        sort_list = list(args)
        sort_list.sort()
        sha = hashlib.sha1()
        sha.update("".join(sort_list).encode())
        return sha.hexdigest()

