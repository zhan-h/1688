import csv
import hashlib
import json
import random
import time
import jsonpath
import requests
from data_1688.API import get_data


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
        """执行数据采集（失败时自动重试一次）"""
        max_retries = 1  # 重试1次，即最多尝试2次
        attempt = 0
        final_all_results = []
        final_total_items = 0

        while attempt <= max_retries:
            attempt += 1
            self.log(f"开始第 {attempt} 次采集尝试...", 'info')

            # ----- 重置本次尝试的状态 -----
            self.is_scraping = True
            all_results = []
            total_items = 0
            completed_requests = 0
            error_occurred = False
            total_pages = end_page - start_page + 1
            total_requests = total_pages * async_count

            try:
                # ----- 原采集逻辑 -----
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
                            itemIds = jsonpath.jsonpath(json_data, '$..list[*].itemId') or []
                            itemIds_API_data = ','.join(itemId for itemId in itemIds)
                            DaySaleNum_30s, addTimes = get_data(itemIds_API_data)

                            for i in range(len(imgUrl)):
                                result = {
                                    "imgUrl": imgUrl[i] if i < len(imgUrl) else "",
                                    "simpleSubject": simpleSubject[i] if i < len(simpleSubject) else "",
                                    "price": price[i] if i < len(price) else "",
                                    "loginId": loginId[i] if i < len(loginId) else "",
                                    "odUrl": odUrl[i] if i < len(odUrl) else "",
                                    "itemIds": itemIds[i] if i < len(itemIds) else "",
                                    "DaySaleNum_30s": DaySaleNum_30s[i] if i < len(DaySaleNum_30s) else "",
                                    "addTimes": addTimes[i] if i < len(addTimes) else "",
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

                    self.log(f"第 {beginpage} 页采集完成，当前累计 {total_items} 条数据", 'info')

            except Exception as e:
                error_occurred = True
                self.log(f"第 {attempt} 次采集发生严重异常: {str(e)}", 'error')
            finally:
                self.is_scraping = False
                self.update_progress(completed_requests, total_requests, items_count=total_items)

            # ----- 判断本次尝试是否成功 -----
            if not error_occurred and total_items > 0:
                self.log(f"第 {attempt} 次采集成功，共采集 {total_items} 条数据", 'info')
                final_all_results = all_results
                final_total_items = total_items
                # 成功时触发完成回调
                if self.callbacks['on_finish']:
                    self.callbacks['on_finish'](final_all_results, final_total_items)
                break
            else:
                if attempt <= max_retries:
                    self.log(f"第 {attempt} 次采集失败（{'异常' if error_occurred else '无数据'}），将重试一次...",
                             'warning')
                    # 继续下一次循环
                else:
                    self.log(f"已达最大尝试次数（{max_retries + 1}次），采集结束，共采集 {total_items} 条数据", 'warning')
                    final_all_results = all_results
                    final_total_items = total_items
                    if self.callbacks['on_finish']:
                        self.callbacks['on_finish'](final_all_results, final_total_items)

        print(final_all_results)
        return final_all_results

    def save_as_json(self, data, filename):
        """保存为JSON格式"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def save_as_csv(self, data, filename):
        """保存为CSV格式"""
        if not data:
            return
        fieldnames = ['imgUrl', 'simpleSubject', 'price', 'loginId', 'odUrl','itemIds', 'DaySaleNum_30s', 'addTimes']
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

class FactoryScraperCore:
    """工厂信息采集核心类"""
    def __init__(self):
        from data_1688.tokens_1688 import get_token, token
        from data_1688.mind import memberIds
        self.get_token = get_token
        self.token = token
        self.memberIds = memberIds
        self.is_scraping = False
        self.callbacks = {
            'on_data': None,
            'on_progress': None,
            'on_log': None,
            'on_finish': None
        }
        # 缓存 token 相关，但每次请求可能需要新 token，我们可以在请求时获取

    def register_callback(self, event, callback):
        if event in self.callbacks:
            self.callbacks[event] = callback

    def log(self, message, level='info'):
        if self.callbacks['on_log']:
            self.callbacks['on_log'](message, level)

    def update_progress(self, current, total, current_member_id=None, items_count=0):
        if self.callbacks['on_progress']:
            self.callbacks['on_progress'](current, total, current_member_id, items_count)

    def on_data_collected(self, data):
        if self.callbacks['on_data']:
            self.callbacks['on_data'](data)

    def on_finish(self, results, total_items):
        if self.callbacks['on_finish']:
            self.callbacks['on_finish'](results, total_items)

    def stop(self):
        self.is_scraping = False
        self.log("正在停止采集任务...", 'warning')

    def _fetch_factory_info(self, member_id):
        """获取单个工厂信息，返回字典或 None"""
        import requests
        import json
        import time
        import re
        _m_h5_tk, _m_h5_tk_enc = self.get_token()
        headers = {
            "referer": "https://sale.1688.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0"
        }
        cookies = {
            "_m_h5_tk": _m_h5_tk,
            "_m_h5_tk_enc": _m_h5_tk_enc,
        }
        inner_params = {
            "memberId": member_id,
            "extendParam": {
                "query": "",
                "trafficSource": "factory_card@detail_pc"
            }
        }
        params_str = json.dumps(inner_params, separators=(',', ':'))
        data = {
            "serviceName": "factoryCoreInfoService",
            "params": params_str
        }
        data_str = json.dumps(data, separators=(',', ':'))
        t = str(int(time.time() * 1000))
        tk_prefix = _m_h5_tk.split("_")[0]
        sign = self.token(tk_prefix, t, data_str)
        request_params = {
            "jsv": "2.6.1",
            "appKey": "12574478",
            "t": t,
            "sign": sign,
            "v": "1.0",
            "type": "originaljsonp",
            "isSec": "0",
            "timeout": "20000",
            "dataType": "jsonp",
            "valueType": "original",
            "api": "mtop.com.alibaba.china.factory.card.common.fn.mtop.tpp.faas",
            "jsonpIncPrefix": "mboxfc",
            "callback": "mtopjsonpmboxfc1",
            "data": data_str
        }
        url = "https://h5api.m.1688.com/h5/mtop.com.alibaba.china.factory.card.common.fn.mtop.tpp.faas/1.0/"
        try:
            response = requests.get(url, headers=headers, cookies=cookies, params=request_params, timeout=10)
            text = response.text
            # 提取公司名称
            names = re.findall(r'"name":"(.*?)"', text)
            filtered_names = [n for n in names if ("公司" in n or n.endswith("厂") or "店" in n or "行" in n)]
            company_name = filtered_names[0] if filtered_names else ""
            # 提取其他字段
            year_started = re.findall(r'"companyYearStarted":(.*?),', text)
            annual_trade = re.findall(r'"annualTradeVolume":(.*?),', text)
            month_product = re.findall(r'"monthProductValue":(.*?),', text)
            address = re.findall(r'"factoryDetailedAddress":(.*?),', text)
            production_service = re.findall(r'"productionService":(.*?),', text)
            info = {
                "memberId": member_id,
                "companyName": str(company_name),
                "companyYearStarted": str(year_started[0]) if year_started else "",
                "annualTradeVolume": str(annual_trade[0]) if annual_trade else "",
                "monthProductValue": str(month_product[0]) if month_product else "",
                "factoryDetailedAddress": str(address[0]) if address else "",
                "productionService": str(production_service[0]) if production_service else "",
                "url": f"https://sale.1688.com/factory/card.html?memberId={member_id}"
            }
            return info
        except Exception as e:
            self.log(f"[{member_id}] 请求失败: {e}", 'error')
            return None

    def scrape(self, category_num, max_pages=50, max_workers=2, delay=0.5):
        """
        采集工厂信息
        :param category_num: 工厂类别数字，如 "311"
        :param max_pages: 最大页码（1-50）
        :param max_workers: 并发线程数
        :param delay: 每次请求后的休眠秒数
        """
        if category_num:
            query = f"mainCate={category_num}"
        else:
            query = ""
        self.is_scraping = True
        self.log(f"开始采集工厂信息，类别: {category_num or '全部'}", 'info')

        # 第一步：获取所有 memberId
        all_member_ids = []
        self.log("正在获取 memberId 列表...", 'info')
        for page in range(1, max_pages + 1):
            if not self.is_scraping:
                break
            ids = self.memberIds(page, query)
            if ids:
                all_member_ids.extend(ids)
            self.update_progress(page, max_pages, None, len(all_member_ids))
            time.sleep(delay)  # 控制请求速度
        self.log(f"共获取到 {len(all_member_ids)} 个 memberId", 'info')
        if not all_member_ids:
            self.log("没有获取到任何 memberId，采集结束", 'warning')
            self.is_scraping = False
            self.on_finish([], 0)
            return
        self.log(f"开始并发获取 {len(all_member_ids)} 个工厂详情（并发数={max_workers}，延时={delay}秒）", 'info')
        # 第二步：并发获取工厂详情
        results = []
        total = len(all_member_ids)
        completed = 0
        from concurrent.futures import ThreadPoolExecutor, as_completed
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_mid = {executor.submit(self._fetch_factory_info, mid): mid for mid in all_member_ids}
            for future in as_completed(future_to_mid):
                if not self.is_scraping:
                    executor.shutdown(wait=False)
                    break
                mid = future_to_mid[future]
                try:
                    data = future.result()
                    if data:
                        results.append(data)
                        self.on_data_collected(data)
                    completed += 1
                    self.update_progress(completed, total, mid, len(results))
                    time.sleep(delay)
                except Exception as e:
                    self.log(f"处理 {mid} 时出错: {e}", 'error')
                    completed += 1
                    self.update_progress(completed, total, mid, len(results))

        self.is_scraping = False
        self.log(f"采集完成，共获取 {len(results)} 条工厂信息", 'info')
        self.on_finish(results, len(results))
        return results