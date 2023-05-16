import asyncio
import io
import json
import os
import re
from datetime import datetime
from typing import Optional, Union

from PIL import Image
from playwright.async_api import async_playwright

import hoshino
from hoshino import util, aiorequests
from hoshino.typing import MessageSegment

# qq_certification_status: bool = True  # 是否开启QQ绿标检测
basic_path = os.path.dirname(__file__)
save_path = os.path.join(basic_path, "temp")
config_path = os.path.join(basic_path, "config.json")
txt_path = os.path.join(basic_path, "certified_websites.txt")
if not os.path.exists(txt_path):
    open(txt_path, "w")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.6) ",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-cn"
}


def gen_ms_img(image: Union[bytes, Image.Image]) -> MessageSegment:
    if isinstance(image, bytes):
        return MessageSegment.image(
            util.pic2b64(Image.open(io.BytesIO(image)))
        )
    else:
        return MessageSegment.image(
            util.pic2b64(image)
        )


def get_present_time() -> int:
    return int(datetime.timestamp(datetime.now()))


async def screen_shot(url: str, time_present: int, gid: str) -> Optional[str or bool]:
    all_domains = get_txt()
    domain = get_domain(url)[0]

    if os.path.exists(config_path):
        try:
            configs = json.load(open(config_path, encoding="utf-8"))
            if gid in configs:
                qq_certification_status = configs[gid]["status"]
            else:
                qq_certification_status = True
        except json.decoder.JSONDecodeError:
            qq_certification_status = True
    else:
        qq_certification_status = True

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
        hoshino.logger.info("正在保存图片...")
        img_path = os.path.join(save_path, f'{time_present}.png')
        await page.screenshot(
            path=img_path,
            full_page=True
        )
        hoshino.logger.info("正在压缩图片...")
        img_convert = Image.open(img_path)
        img_convert.save(img_path, quality=70)
        hoshino.logger.info("图片保存成功！")
        await browser.close()
        return "success"


def update_txt(content: str, file_name: str = "certified_websites.txt"):
    file_path = os.path.join(basic_path, file_name)
    with open(file_path, mode="a+") as f:
        f.writelines("\n" + content)


def get_txt(file_name: str = "certified_websites.txt") -> list:
    file_path = os.path.join(basic_path, file_name)
    with open(file_path, mode="r") as f:
        return f.read().strip().split("\n")


async def get_url_certified_state(url: str) -> dict:
    hoshino.logger.info("正在获取QQ绿标数据...")
    api = f"https://www.yuanxiapi.cn/api/qqurlsec/?url={url}"
    # async with ClientSession(headers=headers, timeout=20) as session:
    try:
        resp = await aiorequests.get(api, headers=headers, timeout=20)
        result = json.loads(await resp.content)
        # async with session.get(url=api) as response:
        #     result = (await response).json()
        return result
    except Exception as e:
        hoshino.logger.error(f"网站{url}获取QQ绿标数据错误。{type(e)}")
        return {}


def get_domain(urls: Optional[list or str] = get_txt) -> list:
    urls = get_txt() if callable(urls) else urls
    urls = [urls] if type(urls) == str else urls
    results = []
    for url in urls:
        regex = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+)'
        result = re.findall(regex, url)
        if not result:
            hoshino.logger.error(f"Url{url} 未能找到域名")
            continue
        results.append(result[0])

    return results
