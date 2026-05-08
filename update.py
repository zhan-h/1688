from github_downloader import download_from_github
import requests
import ssl

# 方法：临时禁用 SSL 验证（猴子补丁）
original_get = requests.get
def patched_get(url, **kwargs):
    kwargs['verify'] = False
    return original_get(url, **kwargs)

requests.get = patched_get

# 调用下载
download_from_github(
    "https://github.com/zhan-h/1688/tree/main/dist",
    dest_folder="./dist"
)

# 恢复（可选）
requests.get = original_get