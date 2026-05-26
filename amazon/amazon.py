import requests
import json
import re

headers = {
    "accept": "text/html,image/webp,*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "content-type": "application/json",
    "device-memory": "8",
    "downlink": "6",
    "dpr": "1.25",
    "ect": "4g",
    "origin": "https://www.amazon.com",
    "priority": "u=1, i",
    "referer": "https://www.amazon.com/s?k=%E7%94%B5%E8%84%91&page=2&language=zh&crid=10T6Q8RK1TUGM&qid=1779173871&sprefix=%2Caps%2C320&xpid=VFxN7FR-J-JU9&ref=sr_pg_2",
    "rtt": "100",
    "sec-ch-device-memory": "8",
    "sec-ch-dpr": "1.25",
    "sec-ch-ua": "\"Chromium\";v=\"148\", \"Microsoft Edge\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
    "sec-ch-ua-full-version-list": "\"Chromium\";v=\"148.0.7778.168\", \"Microsoft Edge\";v=\"148.0.3967.70\", \"Not/A)Brand\";v=\"99.0.0.0\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-ch-ua-platform-version": "\"19.0.0\"",
    "sec-ch-viewport-height": "779",
    "sec-ch-viewport-width": "1114",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0",
    "viewport-width": "1114",
    "x-amazon-rush-fingerprints": "AmazonRushAssetLoader:1202F8AA9B9E3A62A246BF3FA42812770110C222|AmazonRushFramework:3F1238CB9FA596EBA59E26135AD537964DAC7625|AmazonRushRouter:F702738C4F1558FF67504BE28506B41D1ACCBFAC",
    "x-amazon-s-fallback-url": "https://www.amazon.com/-/zh/s?k=%E7%94%B5%E8%84%91&language=zh&crid=10T6Q8RK1TUGM&qid=1779174120&sprefix=%2Caps%2C320&xpid=VFxN7FR-J-JU9&ref=sr_pg_1",
    "x-amazon-s-mismatch-behavior": "FALLBACK",
    "x-amazon-s-swrs-version": "6C9CC599429BECB4815503BE9EDB2932,D41D8CD98F00B204E9800998ECF8427E",
    "x-amzn-flow-closure-id": "1779173827",
    "x-requested-with": "XMLHttpRequest"
}
cookies = {
    "session-id": "135-9196701-8613844",
    "session-id-time": "2082787201l",
    "i18n-prefs": "CNY",
    "lc-main": "zh_CN",
    "sp-cdn": "\"L5Z9:CN\"",
    "ubid-main": "133-7365253-7954535",
    "skin": "noskin",
    "session-token": "GYlm2q7teF9DSX9H6d65EAKKv8LGqnZXp2DTC20Xb7vhfMalFGySy9RYNmIvx/IktbJTJL4VsRSpJi8OdYNKfFYKQlg91n6QRHs325jRhROkHubeotbS2zJXRLwUd7F2+uiVuvy2frOSGVSaGZz9hy4grrrdMEvuqHvVMjZLQMmFEGKKWiQNrwl98HcfTGRzBP6725YY5/PIl2iAG6cEYnT+a6oJc2XP",
    "rxc": "AOd4XpdoWjvtIzQvv04",
    "csm-hit": "tb:RMA98FXGFVD8K8Q2KBWB+s-X2GWBDKZ471B6BCFS9KM|1779174133655&t:1779174133655&adb:adblk_no"
}
url = "https://www.amazon.com/s/query"
params = {
    "crid": "10T6Q8RK1TUGM",
    "k": "电脑",
    "language": "zh",
    "page": "2",
    "qid": "1779174120",
    "ref": "sr_pg_1",
    "sprefix": ",aps,320",
    "xpid": "VFxN7FR-J-JU9"
}
data = {
    "customer-action": "pagination"
}
data = json.dumps(data, separators=(',', ':'))
response = requests.post(url, headers=headers, cookies=cookies, params=params, data=data)

# print(response.text)
html = re.findall(r'<span>(.*?)</span>', response.text)
title = []
for i in html:
    if (re.search('显示(.*?)', i) or re.search('您看到此广告(.*?)', i) or
            re.search('留下广告反馈(.*?)', i)
            or re.search('新用户可获得(.*?)', i) or re.search('在结账时节省(.*?)', i)):
        continue
    elif i.strip() == '':
        continue
    else:
        title.append(i)
        print(i)
