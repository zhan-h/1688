import hashlib
import re
import time
import requests

j = str(time.time() * 1000)


def token(d_token, j, c_data):
    # 计算 MD5 哈希值
    h = "12574478"
    return hashlib.md5(f"{d_token}&{j}&{h}&{c_data}".encode("utf-8")).hexdigest()


# 参数
def get_token():
    d_token = "undefined"
    c_data = '{"appId":39799,"params":"{\\"bizName\\":\\"home_search\\",\\"verticalProductFlag\\":\\"pcfactory\\",\\"method\\":\\"shadeHotKeyword\\",\\"sceneSource\\":\\"factory\\",\\"source\\":\\"pc_shade_hotword\\"}"}'
    sign = token(d_token, j, c_data)
    headers = {
        "accept": "application/json",
        "origin": "https://mind.1688.com",
        "referer": "https://mind.1688.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0"
    }
    url = "https://h5api.m.1688.com/h5/com.alibaba.china.zgc.native.recommend.fn.mtop.tpp.faas/1.0/"
    params = {
        "jsv": "2.7.2",
        "appKey": "12574478",
        "t": j,
        "sign": sign,
        "v": "1.0",
        "type": "originaljson",
        "dataType": "json",
        "timeout": "5000",
        "api": "com.alibaba.china.zgc.native.recommend.fn.mtop.tpp.faas",
        "data": c_data
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.headers["Set-Cookie"]
    _m_h5_tk = re.findall(r"_m_h5_tk=(.*?);", data)[0]
    _m_h5_tk_enc = re.findall(r"_m_h5_tk_enc=(.*?);", data)[0]
    return _m_h5_tk, _m_h5_tk_enc
