import hashlib
import json
import random
import time
import requests
import jsonpath
from API import get_data


def sign(keyword, t):
    """生成签名"""
    sign_origin = f"pcsem{keyword}{t}csb44T%34CiKj&FyRbCBJ"
    return hashlib.md5(sign_origin.encode('utf-8')).hexdigest()


def scrape_1688(keyword, start_page, end_page, async_count):
    """
    1688 爬虫核心函数，采集结果直接打印
    """
    cookies = {
        "cna": "edpjIm1F/EsCAQAAAADwyw2M",
        "_m_h5_tk": "22213af20845b043998e75c2de0653a2_1776094057422",
        "_m_h5_tk_enc": "7d8ddce08a56868afcd4adde0b992489",
        "leftMenuLastMode": "COLLAPSE",
        "plugin_home_downLoad_cookie": "%E4%B8%8B%E8%BD%BD%E6%8F%92%E4%BB%B6",
        "keywordsHistory": "%E6%89%8B%E6%9C%BA%3B%E8%BD%BB%E8%96%84%E5%A4%96%E5%A5%97",
        "cookie1": "UITo4cTe2hqfQiNSfJNmXdmkdgPWUVu%2BOlz%2BPGYUtBo%3D",
        "cookie2": "122d5a9df124fa614a0064ed0cebfdff",
        "cookie17": "UUpgRsIq2v7Y52%2Bz%2FQ%3D%3D",
    }
    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://www.1688.com",
        "referer": "https://www.1688.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    url = "https://p4psearch.1688.com/hamlet/async/v1.json"
    total_items = 0

    for page in range(start_page, end_page + 1):
        for asyncreq in range(1, async_count + 1):
            t = str(int(time.time() * 10000))
            sign_code = sign(keyword, t)
            time.sleep(random.uniform(1, 2))

            params = {
                "beginpage": page,
                "asyncreq": asyncreq,
                "keywords": "",
                "keyword": keyword,
                "sortType": "",
                "descendOrder": "",
                "province": "",
                "city": "",
                "priceStart": "",
                "priceEnd": "",
                "dis": "",
                "ptid": "017700000009773527d8137c21764ec6",
                "exp": "pcSemFumian%3AC%3Bsidebar%3AC%3BpcDacuIconExp%3AB%3BpcCpxGuessExp%3AB%3Bqztf%3AF%3BpcCpxCpsExp%3AB%3Bwysiwyg%3AB%3BhotBangdanExp%3AB%3BpcSemWwClick%3AA%3Basst%3AD%3BpcSemDownloadPlugin%3AA",
                "cosite": "bingjj",
                "salt": t,
                "sign": sign_code,
                "hmaTid": "3",
                "hmaQuery": "graphDataQuery",
                "pidClass": "pc_list_336",
                "cpx": "cpc%2Ccpt%2Cfree%2Cnature",
                "api": "pcSearch",
                "pv_id": ""
            }

            try:
                resp = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=10)
                data = resp.json()
                imgUrl = jsonpath.jsonpath(data, '$..list[*].imgUrl') or []
                simpleSubject = jsonpath.jsonpath(data, '$..simpleSubject') or []
                price = jsonpath.jsonpath(data, '$..list[*].price') or []
                loginId = jsonpath.jsonpath(data, '$..loginId') or []
                odUrl = jsonpath.jsonpath(data, '$..odUrl') or []
                itemIds = jsonpath.jsonpath(data, '$..list[*].itemId') or []
                itemIds_API_data = ','.join(itemId for itemId in itemIds)
                DaySaleNum_30s, addTimes = get_data(itemIds_API_data)

                # print(itemIds)
                for i in range(len(imgUrl)):
                    item = {
                        "imgUrl": imgUrl[i] if i < len(imgUrl) else "",
                        "simpleSubject": simpleSubject[i] if i < len(simpleSubject) else "",
                        "price": price[i] if i < len(price) else "",
                        "loginId": loginId[i] if i < len(loginId) else "",
                        "odUrl": odUrl[i] if i < len(odUrl) else "",
                        "itemIds": itemIds[i] if i < len(itemIds) else "",
                        "DaySaleNum_30s": DaySaleNum_30s[i] if i < len(DaySaleNum_30s) else "",
                        "addTimes": addTimes[i] if i < len(addTimes) else "",
                    }
                    # 直接打印每条数据
                    print(json.dumps(item, ensure_ascii=False))
                    total_items += 1

                print(f"[进度] 页 {page} / asyncreq {asyncreq} → 本次获取 {len(imgUrl)} 条，累计 {total_items} 条")
            except Exception as e:
                print(f"[错误] {e}")

    # print(f"\n采集完成，共获取 {total_items} 条数据")


# 使用示例
if __name__ == "__main__":
    scrape_1688(keyword="手机壳", start_page=1, end_page=2, async_count=2)
