import random
import string


def get_random_str(num: int) -> str:
    """
    获取指定长度的随机内容
    :param num: 指定获取随机内容的长度
    :return: 返回生成的随机内容
    """
    str_list = [random.choice(string.digits + string.ascii_letters) for i in range(num)]
    random_str = ''.join(str_list)
    return random_str
