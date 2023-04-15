import os
from hoshino import Service, priv, R
from hoshino.typing import CQEvent
from .utils import *
from nonebot import MessageSegment

sv_help = """
网页截图/预览

自动预览，
当有以http/https开头的链接会自动发送网页截图

手动网页截图，
#[网页截图/预览] https://www.baidu.com
""".strip()
sv = Service(
    name="webscreenshot",  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.ADMIN,  # 管理权限
    visible=True,  # 可见性
    enable_on_default=True,  # 默认启用
    bundle="功能性",  # 分组归类
    help_=sv_help  # 帮助说明
)


@sv.on_fullmatch(("网页截图帮助", "网页预览帮助"), only_to_me=False)
async def sendHelp(bot, ev):
    await bot.send(ev, sv_help)


@sv.on_prefix(('网页截图', '网页预览', '截图', '预览'), only_to_me=False)
async def screenshot(bot, ev: CQEvent):
    uid = str(ev.user_id)
    url = str(ev.message.extract_plain_text()).strip()
    message_id = str(ev.message_id)
    save_path = get_path("temp")
    nowtime = getNowtime()
    # CQ:reply,id={message_id}][CQ:at,qq={uid}]，
    result = await screen_shot(url, nowtime)
    if not result:
        await bot.finish(ev, f"[CQ:reply,id={message_id}][CQ:at,qq={uid}]{result}")

    await bot.send(ev, f"{MessageSegment.image(f'file:///{save_path}/{nowtime}.png')}")
    os.remove(fr'{save_path}\{nowtime}.png')
    MessageSegment.reply()


@sv.on_prefix(('http', 'https'), only_to_me=False)
async def preview(bot, ev: CQEvent):
    url = str(ev.raw_message).strip()
    uid = str(ev.user_id)
    nowtime = getNowtime()
    message_id = str(ev.message_id)
    save_path = get_path("temp")
    result = await screen_shot(url, nowtime)
    if result is not None:
        await bot.finish(ev, f"[CQ:reply,id={message_id}][CQ:at,qq={uid}]{result}")
    await bot.send(ev, f"{MessageSegment.image(f'file:///{save_path}/{nowtime}.png')}")
    os.remove(fr'{save_path}\{nowtime}.png')
