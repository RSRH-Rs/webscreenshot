import hoshino.config
from hoshino import Service, priv, HoshinoBot
from hoshino.typing import CQEvent
from .utils import *

sv_help = """
网页截图/预览

自动预览，
当有以http/https开头的链接会自动发送网页截图

手动网页截图，
#[网页截图/预览] https://www.baidu.com
""".strip()
sv = Service(
    name="网页截图",  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.ADMIN,  # 管理权限
    visible=False,  # 可见性
    enable_on_default=False,  # 默认启用
    bundle="功能",  # 分组归类
    help_=sv_help  # 帮助说明
)


@sv.on_fullmatch("帮助网页截图")
async def bangzhu(bot: HoshinoBot, ev: CQEvent):
    await bot.send(ev, sv_help)


@sv.on_prefix(('网页截图', '网页预览', '截图', '预览'))
async def screenshot(bot: HoshinoBot, ev: CQEvent):
    url = ev.message.extract_plain_text().strip()
    gid = str(ev.group_id)
    message_id = ev.message_id
    time_present = get_present_time()
    result = await screen_shot(url, time_present, gid)
    if result != "success":
        await bot.finish(ev, MessageSegment.reply(message_id) + result)
        # await bot.finish(ev, f"[CQ:reply,id={message_id}][CQ:at,qq={uid}]{result}")
    img_path = os.path.join(save_path, f"{time_present}.png")
    hoshino.logger.info(img_path)
    await bot.send(ev, f"{gen_ms_img(Image.open(img_path))}")
    os.remove(img_path)
    # print("图片移除成功！")


@sv.on_prefix(('http://', 'https://'))  # noqa
async def preview(bot: HoshinoBot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        return
    url = ev.raw_message.strip()
    gid = str(ev.group_id)
    time_present = get_present_time()
    message_id = int(ev.message_id)
    result = await screen_shot(url, time_present, gid)
    if result != "success":
        await bot.finish(ev, MessageSegment.reply(message_id) + result)
    img_path = os.path.join(save_path, f"{time_present}.png")
    hoshino.logger.info(img_path)
    await bot.send(ev, f"{gen_ms_img(Image.open(img_path))}")
    os.remove(img_path)
    # print("图片移除成功！")


@sv.on_prefix("切换绿标检测状态")
async def switch_website_mark(bot: HoshinoBot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '此命令仅群管可用~')
    msg = ev.message.extract_plain_text().strip()
    status = True
    if re.match("关闭|false", msg, re.I):
        status = False
    basic_config = {
        "status": status
    }
    gid = str(ev.group_id)
    if os.path.exists(config_path):
        try:
            configs = json.load(open(config_path, encoding="utf-8"))
            if gid in configs:
                if not msg:
                    configs[gid]["status"] = not configs[gid]["status"]
                else:
                    configs[gid]["status"] = status
                with open(config_path, "w", encoding="utf-8") as f:
                    f.write(json.dumps(configs, indent=2, ensure_ascii=False))
                await bot.send(ev, f"本群绿标检测状态已切换为{status}")
                return
            else:
                configs[gid] = basic_config
                with open(config_path, "w", encoding="utf-8") as f:
                    f.write(json.dumps(configs, indent=2, ensure_ascii=False))
                await bot.send(ev, f"本群绿标检测状态已切换为{status}")
                return

        except json.decoder.JSONDecodeError:
            pass

    configs = {
        gid: basic_config
    }
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(configs, indent=2, ensure_ascii=False))
    await bot.send(ev, f"本群绿标检测状态已切换为{status}")
