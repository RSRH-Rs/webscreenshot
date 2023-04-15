import os
import re
import requests
from playwright.async_api import async_playwright
import time
import asyncio
import os
from datetime import datetime
from requests import get
from typing import Optional

file_path = "temp"


def getNowtime() -> int:
    return int(datetime.timestamp(datetime.now()))


async def screen_shot(url: str, nowTime: int) -> Optional[str or bool]:
    all_domains = get_txt()
    domain = get_domain(url)[0]
    save_path = get_path(file_path)

    if domain not in all_domains:
        status = get_url_certified_state(url)
        status_type = status["type"]
        status_msg = status['msg'] if "msg" in status.keys() else 000
        if status_type != 1:
            return f"{'该网站' if status_type == 1 or status_type == 2 else ''}{status_msg}"
        else:
            update_txt(domain)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            await page.goto(url)
        except:
            return f"访问网站超时"
        await asyncio.sleep(1)
        await page.screenshot(path=fr"{save_path}\{nowTime}.png", full_page=True)
        await browser.close()


def update_txt(content: str, file_name: str = "certified_websites.txt"):
    file_path = get_path(file_name)
    with open(file_path, mode="a+") as f:
        f.writelines("\n" + content)


def get_txt(file_name: str = "certified_websites.txt") -> list:
    file_path = get_path(file_name)
    with open(file_path, mode="r") as f:
        return f.read().strip().split("\n")



def get_url_certified_state(url: str) -> int:
    print("getting response")
    api = "https://www.yuanxiapi.cn/api/qqurlsec/?url=%s"
    response = get(url=api % url).json()
    return response


def get_path(*paths) -> str:
    return os.path.join(os.path.dirname(__file__), *paths)


def get_domain(urls: Optional[list or str] = get_txt) -> list:
    urls = get_txt() if callable(urls) else urls
    urls = [urls] if type(urls) == str else urls
    results = []
    for url in urls:
        if not url:
            continue
        result = re.search(r"(?<=[htps]://)[.\w-]*(:\d{,8})?((?=/)|(?!/))", url)
        results.append(result.group(0))

    return results
