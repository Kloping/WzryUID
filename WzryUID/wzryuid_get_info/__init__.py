from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger
from gsuid_core.utils.database.api import get_uid

from .draw_get_info import draw_info_img
from .draw_online_list import draw_online_list_img
from .draw_online_list import draw_online_one_img
from ..utils.error_reply import get_error
from ..utils.database.models import WzryBind

sv_wzry_get_info = SV('查询王者荣耀主页详细信息')
sv_wzry_online_list = SV('查看已绑定的在线详情')
sv_wzry_online_one = SV('窥视某人的在线详情')


@sv_wzry_get_info.on_command('当前段位')
async def send_wzry_history(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev, WzryBind)
    if uid is None:
        return await bot.send(get_error(-41))
    logger.info(f'[当前段位] uid:{uid}')
    im = await draw_info_img(ev.user_id, uid)
    await bot.send(im)


@sv_wzry_online_list.on_command('在线列表')
async def send_wzry_online_list(bot: Bot, ev: Event):
    logger.info("[在线列表]开始查询")
    im = await draw_online_list_img(ev.bot_id)
    await bot.send(im)


@sv_wzry_online_one.on_command(('王者窥视', 'wzks'))
async def send_wzry_online_list(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev, WzryBind)
    if uid is None:
        return await bot.send(get_error(-41))
    logger.info("[wzks]开始查询")
    im = await draw_online_one_img(uid)
    await bot.send(im)
