import csv
import hashlib
import json
import random
import time

import jsonpath
import requests


def sign(keyword, t):
    """生成签名"""
    sign_origin = f"pcsem{keyword}{t}csb44T%34CiKj&FyRbCBJ"
    return hashlib.md5(sign_origin.encode('utf-8')).hexdigest()


class AlibabaScraperCore:
    """1688爬虫核心类"""

    def __init__(self):
        self.cookies = {
            "cna": "edpjIm1F/EsCAQAAAADwyw2M",
            "mtop_partitioned_detect": "1",
            "_m_h5_tk": "22213af20845b043998e75c2de0653a2_1776094057422",
            "_m_h5_tk_enc": "7d8ddce08a56868afcd4adde0b992489",
            "xlly_s": "1",
            "leftMenuLastMode": "COLLAPSE",
            "plugin_home_downLoad_cookie": "%E4%B8%8B%E8%BD%BD%E6%8F%92%E4%BB%B6",
            "keywordsHistory": "%E6%89%8B%E6%9C%BA%3B%E8%BD%BB%E8%96%84%E5%A4%96%E5%A5%97",
            "cookie1": "UITo4cTe2hqfQiNSfJNmXdmkdgPWUVu%2BOlz%2BPGYUtBo%3D",
            "cookie2": "122d5a9df124fa614a0064ed0cebfdff",
            "cookie17": "UUpgRsIq2v7Y52%2Bz%2FQ%3D%3D",
            "sgcookie": "E100ok%2B%2FmtBjC52qBu%2Ft3k%2BDJiGkt9yDX%2FOnDTEnfQku7ca9xQ%2Fg4A1tcnC%2BTlDQBN09MaCGF%2BqCocy1rAOu6FvhjO%2B0704Ufk%2F43MRB%2BCAARxU%3D",
            "t": "57cbd582db7a84c559cf18831ac12556",
            "_tb_token_": "7155b5db75a78",
            "sg": "131",
            "csg": "0cf87684",
            "lid": "tb346655251",
            "unb": "2210657170403",
            "_csrf_token": "1776086792952",
        }

        self.headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://www.1688.com",
            "referer": "https://www.1688.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        self.url = "https://p4psearch.1688.com/hamlet/async/v1.json"
        self.is_scraping = False
        self.callbacks = {
            'on_data': None,  # 每采集到一条数据时回调
            'on_progress': None,  # 进度更新回调
            'on_log': None,  # 日志回调
            'on_finish': None  # 采集完成回调
        }

    def register_callback(self, event, callback):
        """注册回调函数"""
        if event in self.callbacks:
            self.callbacks[event] = callback

    def log(self, message, level='info'):
        """发送日志"""
        if self.callbacks['on_log']:
            self.callbacks['on_log'](message, level)

    def update_progress(self, current, total, page=None, async_num=None, items_count=0):
        """更新进度"""
        if self.callbacks['on_progress']:
            self.callbacks['on_progress'](current, total, page, async_num, items_count)

    def on_data_collected(self, data):
        """数据采集回调"""
        if self.callbacks['on_data']:
            self.callbacks['on_data'](data)

    def stop(self):
        """停止采集"""
        self.is_scraping = False
        self.log("正在停止采集任务...", 'warning')

    def scrape(self, keyword, start_page, end_page, async_count):
        """执行数据采集"""
        self.is_scraping = True
        self.log(f"开始采集关键词 '{keyword}' 的数据...", 'info')

        total_pages = end_page - start_page + 1
        total_requests = total_pages * async_count
        completed_requests = 0
        all_results = []
        total_items = 0

        try:
            for beginpage in range(start_page, end_page + 1):
                if not self.is_scraping:
                    self.log("采集任务已停止", 'warning')
                    break

                for asyncreq in range(1, async_count + 1):
                    if not self.is_scraping:
                        break

                    t = str(int(time.time() * 10000))
                    sign_code = sign(keyword, t)
                    time.sleep(random.uniform(1, 2))

                    params = {
                        "beginpage": beginpage,
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
                        response = requests.get(self.url, headers=self.headers,
                                                cookies=self.cookies, params=params, timeout=10)
                        json_data = response.json()
                        imgUrl = jsonpath.jsonpath(json_data, '$..list[*].imgUrl') or []
                        simpleSubject = jsonpath.jsonpath(json_data, '$..simpleSubject') or []
                        price = jsonpath.jsonpath(json_data, '$..list[*].price') or []
                        loginId = jsonpath.jsonpath(json_data, '$..loginId') or []
                        odUrl = jsonpath.jsonpath(json_data, '$..odUrl') or []

                        for i in range(len(imgUrl)):
                            result = {
                                "imgUrl": imgUrl[i] if i < len(imgUrl) else "",
                                "simpleSubject": simpleSubject[i] if i < len(simpleSubject) else "",
                                "price": price[i] if i < len(price) else "",
                                "loginId": loginId[i] if i < len(loginId) else "",
                                "odUrl": odUrl[i] if i < len(odUrl) else ""
                            }

                            all_results.append(result)
                            total_items += 1
                            self.on_data_collected(result)

                            if total_items % 10 == 0:
                                self.log(f"已采集 {total_items} 条数据", 'info')

                    except Exception as e:
                        self.log(f"请求失败: {str(e)}", 'error')

                    completed_requests += 1
                    self.update_progress(completed_requests, total_requests, beginpage, asyncreq, total_items)

                self.log(f"第 {beginpage} 页采集完成，共采集 {total_items} 条数据", 'info')

        except Exception as e:
            self.log(f"采集过程出错: {str(e)}", 'error')
        finally:
            self.is_scraping = False
            self.log(f"采集任务结束！共采集 {total_items} 条数据", 'info')

            if self.callbacks['on_finish']:
                self.callbacks['on_finish'](all_results, total_items)

            self.update_progress(total_requests, total_requests, items_count=total_items)

        return all_results

    def save_as_json(self, data, filename):
        """保存为JSON格式"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def save_as_csv(self, data, filename):
        """保存为CSV格式"""
        if not data:
            return
        fieldnames = ['imgUrl', 'simpleSubject', 'price', 'loginId', 'odUrl']
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)