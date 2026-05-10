import hashlib
import time
import re
import requests

def get_token():
    t = str(time.time() * 1000)
    data = {
        "data": "{\"piUrl\":\"https://h5.m.goofish.com/wow/moyu/moyu-project/xy-site/pages/announcement\"}"
    }

    def sign(token, timestamp, input_data):
        h = "34839810"
        return hashlib.md5(f"{token}&{timestamp}&{h}&{input_data}".encode("utf-8")).hexdigest()

    headers = {
        "Origin": "https://www.goofish.com",
        "Referer": "https://www.goofish.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0",
    }
    url = "https://h5api.m.goofish.com/h5/mtop.gaia.nodejs.gaia.idle.data.gw.v2.index.get/1.0/"
    params = {
        "jsv": "2.7.2",
        "appKey": "34839810",
        "t": f"{t}",
        "sign": sign("undefined",t,data),
        "v": "1.0",
        "type": "originaljson",
        "accountSite": "xianyu",
        "dataType": "json",
        "timeout": "20000",
        "api": "mtop.gaia.nodejs.gaia.idle.data.gw.v2.index.get",
        "sessionOption": "AutoLoginOnly",
        "spm_cnt": "a21ybx.search.0.0",
        "spm_pre": "a21ybx.home.searchHistory.2.4c053da6QZmG7c",
        "log_id": "4c053da6QZmG7c"
    }

    response = requests.post(url, headers=headers, params=params, data=data)
    data = response.headers["Set-Cookie"]
    _m_h5_tk = re.findall(r"_m_h5_tk=(.*?);", data)[0]
    _m_h5_tk_enc = re.findall(r"_m_h5_tk_enc=(.*?);", data)[0]
    return _m_h5_tk, _m_h5_tk_enc
