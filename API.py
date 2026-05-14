import requests
import json
import jsonpath


def get_data(item_id):
    url = "https://api.aliprice.com/chrome/items/get1688ListItemsInfo"

    headers = {
        "Host": "api.aliprice.com",
        "Browser": "edge",
        "Ext_id": "80354",
        "Ext-Id": "80354",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0",
        "Accept": "application/json, text/plain, */*",
        "Channel": "edge",
        "Content-Type": "application/json;charset=UTF-8",
        "Version": "3.7.4",
        "Platform": "1688",
        "Origin": "chrome-extension://mdlcdgmcaceammhekheabondocjocike",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Priority": "u=1, i"
    }

    cookies = {
        "m-info": '[{"platform":"1688","version":"3.7.4","browser":"edge","m":"bsfc","t":1778517676037}]',
        "e-info": '[{"e-name":"1688","adid":"100","version":"3.7.4","ext_id":"80354"}]',
        "plugin_ext": "100",
        "language": "chinese",
        "province_code": "Guangdong",
        "is_reto": "1",
        "crossborder": "1",
        "agent": "0",
        "PHPSESSID": "q53u0hkg4lgm8rkqka3nkggkf1",
        "ali_check": "AukBNpoC8lLXb2M01778481678",
        "first_view": "1",
        "cookie_id": "l94WemELVDzcbyk01778481679",
        "currency": "USD",
        "is_coo": "1",
        "_ga": "GA1.1.1779885574.1778481680",
        "_ga_MYJXW09T9P": "GS2.1.s1778481679$o1$g0$t1778481686$j53$l0$h0",
        "_ga_8CWVNBE4QY": "GS2.1.s1778481679$o1$g0$t1778481686$j53$l0$h0",
        "_ga_YKWTEGEBP2": "GS2.1.s1778481679$o1$g0$t1778481686$j53$l0$h0",
        "acw_tc": "b7e8eba217784854053775805e5b029d6509e8584dbd9068a60a005609",
        "cdn_sec_tc": "b7e8eba217784854053775805e5b029d6509e8584dbd9068a60a005609"
    }

    data = {
        "sku_ids": f"{item_id}"
    }

    response = requests.post(url, headers=headers, cookies=cookies, json=data, timeout=10)

    if response.status_code == 200:
        # 处理 UTF-8 BOM
        content = response.content.decode('utf-8-sig')
        result = json.loads(content)
        # print("获取成功，数据：")
        DaySaleNum_30s = []
        addTimes = []
        DaySaleNum_30 = jsonpath.jsonpath(result, '$..30DaySaleNum')
        addTime = jsonpath.jsonpath(result, '$..addTime')
        for i in range(len(DaySaleNum_30)):
            DaySaleNum_30s.append(int(DaySaleNum_30[i]))
            addTimes.append(addTime[i].split("(")[0])
            # print(f"月代销：{DaySaleNum_30[i]}，上架时间：{addTime[i]}")
        return DaySaleNum_30s, addTimes
    else:
        print(f"请求失败，状态码：{response.status_code}")
        # 打印前500字符以便调试
        print("响应内容预览：", response.text[:500])
