import hashlib
import json
import time
import jsonpath
import requests
from tokens import get_token

class GoofishScraperCore:
    def __init__(self):
        self.is_scraping = False
        self.callbacks = {'on_data': None, 'on_progress': None, 'on_log': None, 'on_finish': None}
        self._m_h5_tk, self._m_h5_tk_enc = get_token()
        self.t = int(time.time() * 1000)
        # token 前缀
        self.token = self._m_h5_tk.split("_")[0] if "_" in self._m_h5_tk else self._m_h5_tk

    def register_callback(self, event, callback):
        if event in self.callbacks:
            self.callbacks[event] = callback

    def log(self, message, level='info'):
        if self.callbacks['on_log']:
            self.callbacks['on_log'](message, level)

    def update_progress(self, current, total, page=None, async_num=None, items_count=0):
        if self.callbacks['on_progress']:
            self.callbacks['on_progress'](current, total, page, async_num, items_count)

    def on_data_collected(self, data):
        if self.callbacks['on_data']:
            self.callbacks['on_data'](data)

    def stop(self):
        self.is_scraping = False
        self.log("正在停止采集任务...", 'warning')

    def sign(self, timestamp, input_data):
        """签名方法"""
        h = "34839810"
        sign_str = self.token + "&" + str(timestamp) + "&" + h + "&" + input_data
        return hashlib.md5(sign_str.encode("utf-8")).hexdigest()

    def scrape(self, keyword, page_numbers):
        """
        执行采集
        :param keyword: 搜索关键词
        :param page_numbers: 要采集的页数（从第1页到第page_numbers页）
        """
        self.is_scraping = True
        self.log(f"开始采集关键词 '{keyword}' 的数据，共 {page_numbers} 页", 'info')

        all_results = []
        total_items = 0
        total_pages = page_numbers

        cookies = {
            "cna": "YuFnIu4i1hABASQJilXOb86I",
            "_m_h5_tk": self._m_h5_tk,
            "_m_h5_tk_enc": self._m_h5_tk_enc,
        }

        headers = {
            "Origin": "https://www.goofish.com",
            "Referer": "https://www.goofish.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0",
        }

        url = "https://h5api.m.goofish.com/h5/mtop.taobao.idlemtopsearch.pc.search/1.0/"

        for page in range(1, page_numbers + 1):
            if not self.is_scraping:
                break

            # 构造 data（与原始脚本完全一致）
            data_str = '{"pageNumber":%d,"keyword":"%s","fromFilter":false,"rowsPerPage":30,"sortValue":"","sortField":"","customDistance":"","gps":"","propValueStr":{},"customGps":"","searchReqFromPage":"pcSearch","extraFilterValue":"{}","userPositionJson":"{}"}' % (page, keyword)
            data = {"data": data_str}

            params = {
                "jsv": "2.7.2",
                "appKey": "34839810",
                "t": self.t,                      # 使用固定的时间戳
                "sign": self.sign(self.t, data_str),
                "v": "1.0",
                "type": "originaljson",
                "accountSite": "xianyu",
                "dataType": "json",
                "timeout": "20000",
                "api": "mtop.taobao.idlemtopsearch.pc.search",
                "sessionOption": "AutoLoginOnly",
                "spm_cnt": "a21ybx.search.0.0",
                "spm_pre": "a21ybx.home.searchActivate.3.4c053da6VxXLJY",
                "log_id": "4c053da6VxXLJY"
            }

            try:
                response = requests.post(url, headers=headers, cookies=cookies, params=params, data=data, timeout=15)
                if response.status_code != 200:
                    self.log(f"第 {page} 页请求失败，状态码: {response.status_code}", 'error')
                    continue

                data_json = response.json()
                # 按照原始脚本的遍历范围 0-30（实际最多30条，但不影响）
                page_item_count = 0
                for i in range(0, 31):
                    if not self.is_scraping:
                        break
                    # 使用 jsonpath 按照原始路径提取
                    item = jsonpath.jsonpath(data_json, f'$..data.resultList[{i}].data.item')
                    if not item or not item[0]:
                        continue
                    item_data = item[0]

                    picUrl = jsonpath.jsonpath(item_data, '$..main.exContent.picUrl')
                    area = jsonpath.jsonpath(item_data, '$..main.exContent.area')
                    soldPrice = jsonpath.jsonpath(item_data, '$..main.exContent.detailParams.soldPrice')
                    title = jsonpath.jsonpath(item_data, '$..main.exContent.detailParams.title')
                    userNickName = jsonpath.jsonpath(item_data, '$..main.exContent.userNickName')
                    publishTime = jsonpath.jsonpath(item_data, '$..clickParam.args.publishTime')
                    targetUrl = jsonpath.jsonpath(item_data, '$..main.targetUrl')

                    # 判断必要字段是否存在（原始脚本中 area,soldPrice,title,userNickName,publishTime 非空）
                    if area and soldPrice and title and userNickName and publishTime is not None:
                        detail_url = f"https://www.goofish.com/{targetUrl[0].replace('fleamarket://', '')}"
                        result = {
                            "picUrl": picUrl[0] if picUrl else "",
                            "area": area[0],
                            "price": soldPrice[0],
                            "title": title[0],
                            "seller": userNickName[0],
                            "publishTime": publishTime[0],
                            "url": detail_url
                        }
                        all_results.append(result)
                        total_items += 1
                        page_item_count += 1
                        self.on_data_collected(result)

                self.log(f"第 {page} 页采集完成，本页获取 {page_item_count} 条", 'info')
                self.update_progress(page, total_pages, page, items_count=total_items)

            except Exception as e:
                self.log(f"第 {page} 页请求异常: {str(e)}", 'error')

            time.sleep(1)  # 适当延时

        self.is_scraping = False
        self.log(f"采集任务结束！共采集 {total_items} 条数据", 'info')
        if self.callbacks['on_finish']:
            self.callbacks['on_finish'](all_results, total_items)

        return all_results


    @staticmethod
    def save_as_json(data, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def save_as_csv(data, filename):
        if not data:
            return
        import csv
        fieldnames = ['picUrl', 'area', 'price', 'title', 'seller', 'publishTime', 'url']
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)