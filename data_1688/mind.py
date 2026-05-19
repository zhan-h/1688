import re
import json
import time
import requests
import jsonpath
from data_1688.tokens_1688 import get_token, token

headers = {
    "accept": "application/json",
    "origin": "https://mind.1688.com",
    "referer": "https://mind.1688.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0"
}

_m_h5_tk, _m_h5_tk_enc = get_token()
cookies = {
    "_m_h5_tk": _m_h5_tk,
    "_m_h5_tk_enc": _m_h5_tk_enc,
}

def memberIds(pageNo, query):
    """获取单页的 memberId 列表"""
    inner_params = {
        "pageNo": pageNo,
        "pageSize": 20,
        "from": "PC",
        "showType": "transverse",
        "trafficSource": "pc_index_recommend",
        "sort": "mix",
        "query": query,
        "params": {
            "pageNo": pageNo,
            "pageSize": 20,
            "from": "PC",
            "showType": "transverse",
            "trafficSource": "pc_index_recommend",
            "sort": "mix",
            "query": query
        }
    }
    params_str = json.dumps(inner_params, separators=(',', ':'))

    data = {
        "serviceName": "tpFacRecommendService",
        "params": params_str
    }
    data_str = json.dumps(data, separators=(',', ':'))

    t = str(int(time.time() * 1000))
    tk_prefix = _m_h5_tk.split("_")[0]
    sign = token(tk_prefix, t, data_str)

    params = {
        "jsv": "2.7.2",
        "appKey": "12574478",
        "t": t,
        "sign": sign,
        "v": "1.0",
        "type": "originaljson",
        "dataType": "json",
        "timeout": "5000",
        "api": "com.alibaba.china.zgc.native.recommend.fn.mtop.tpp.faas",
        "data": data_str
    }

    url = "https://h5api.m.1688.com/h5/com.alibaba.china.zgc.native.recommend.fn.mtop.tpp.faas/1.0/"
    memberId_list = []
    try:
        response = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=10)
        if response.status_code == 200:
            result = response.json()
            pcUrlWithProcessItems = jsonpath.jsonpath(result, '$..pcUrlWithProcessItems')
            if pcUrlWithProcessItems:
                for item in pcUrlWithProcessItems:
                    matches = re.findall('memberId=(.*?)&', item)
                    if matches:
                        memberId_list.append(matches[0])
            print(f"[第{pageNo}页] 获取到 {len(memberId_list)} 个 memberId")
            return memberId_list
        else:
            print(f"[第{pageNo}页] 请求失败，状态码: {response.status_code}")
            return []
    except Exception as e:
        print(f"[第{pageNo}页] 异常: {e}")
        return []
