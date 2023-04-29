import os
import re
from playwright.async_api import async_playwright
import asyncio
import os
from datetime import datetime
from requests import get
from typing import Optional
import hoshino
from .config import qq_certification_status
from aiohttp.client import ClientSession

file_path = "temp"
qq_certification_status:bool = qq_certification_status

def getNowtime() -> int:
    return int(datetime.timestamp(datetime.now()))


async def screen_shot(url: str, nowTime: int) -> Optional[str or bool]:
    all_domains = get_txt()
    domain = get_domain(url)[0]
    save_path = get_path(file_path)

    if qq_certification_status:
        if domain not in all_domains:
            status = await get_url_certified_state(url)
            if not status:
                return "获取QQ绿标数据错误"
            status_type = status["type"] if "type" in status.keys() else 000
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
        except Exception as e:
            return f"访问网站超时{type(e)}`{e}`"
        await asyncio.sleep(1)
        hoshino.logger.error("[Warning]正在保存图片...")
        await page.screenshot(path=fr"{get_path(save_path,str(nowTime))}.png", full_page=True)
        hoshino.logger.error("[Warning]图片保存成功！")
        await browser.close()
        return "success"


def update_txt(content: str, file_name: str = "certified_websites.txt"):
    file_path = get_path(file_name)
    with open(file_path, mode="a+") as f:
        f.writelines("\n" + content)


def get_txt(file_name: str = "certified_websites.txt") -> list:
    file_path = get_path(file_name)
    with open(file_path, mode="r") as f:
        return f.read().strip().split("\n")



async def get_url_certified_state(url: str) -> dict:
    hoshino.logger.error("[Warning]正在获取QQ绿标数据...")
    api = "https://www.yuanxiapi.cn/api/qqurlsec/?url=%s"
    async with ClientSession() as session:
        try:
            async with session.get(url=api%url) as response:
                result = await response.json()
                return result
        except Exception as e:
            hoshino.logger.error(f"[Error] 网站{url}获取QQ绿标数据错误。{type(e)}")
            return {}

def get_path(*paths) -> str:
    return os.path.join(os.path.dirname(__file__), *paths)


def get_domain(urls: Optional[list or str] = get_txt) -> list:
    urls = get_txt() if callable(urls) else urls
    urls = [urls] if type(urls) == str else urls
    results = []
    for url in urls:
        regex = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+)'
        result = re.findall(regex, url)
        if not result:
            hoshino.logger.error(f"[Error] Url{url} 未能找到域名")
            continue
        results.append(result[0])

    return results
