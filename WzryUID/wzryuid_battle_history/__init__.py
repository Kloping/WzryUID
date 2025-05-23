from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger
from gsuid_core.utils.database.api import get_uid

from ..utils.error_reply import get_error
from ..utils.database.models import WzryBind
from .draw_battle_history import draw_history_img
from .draw_battle_one_history import draw_history_one_img

sv_wzry_history = SV('查询王者荣耀战绩')


@sv_wzry_history.on_command(('查荣耀', 'cry'))
async def send_wzry_history(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev, WzryBind)
    if uid is None:
        return await bot.send(get_error(-41))
    name = ev.text.strip()
    hn = None
    option = 0
    if name.startswith("排位"):
        option = 1
    elif name.startswith("标准"):
        option = 2
    elif name.startswith("娱乐"):
        option = 3
    elif name.startswith("巅峰"):
        option = 4
    else:
        hn = name

    logger.info(f'[查荣耀] uid:{uid}')
    if hn is None or hn == '':
        im = await draw_history_img(ev.user_id, uid, option)
    else:
        im = await draw_history_one_img(ev.user_id, uid, hn)
    await bot.send(im)
