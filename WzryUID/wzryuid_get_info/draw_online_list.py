from pathlib import Path
from typing import Union
import numpy as np
import time
from ..utils.database.models import WzryBind
from ..utils.wzry_api import wzry_api

TEXT_PATH = Path(__file__).parent / 'texture2d'


async def draw_online_list_img(bot_id: str) -> Union[str, bytes]:
    uids = await WzryBind.get_all_uid_list_by_game(bot_id)
    if len(uids) == 0:
        return '暂无绑定'
    uids = np.unique(uids)
    result = "在线列表↓↓↓↓↓↓\n"
    for yd_user_id in uids:
        oData = await wzry_api.get_user_role(yd_user_id)
        if isinstance(oData, int):
            return get_error(oData)
        data = oData[0]
        # 获取资料数据
        profile_data = await wzry_api.get_user_profile(yd_user_id, data['roleId'])
        # roleCard
        roleCard = profile_data['roleCard']
        if roleCard['gameOnline'] == 1:
            bhd = await wzry_api.get_battle_history(yd_user_id, 10)
            if isinstance(bhd, int):
                online = '🟢在线'
            elif bhd['isGaming']:
                online = f"🟠{bhd['gaming']['mapName']}-{bhd['gaming']['title']}"
            else:
                online = '🟢在线'
        else:
            online = '⚪离线'
        result = result + (f"{roleCard['areaName']}-{roleCard['roleJobName']}\n"
                           f"\t{roleCard['roleName']} {roleCard['serverName']}\t{online}\n")
    return result


async def draw_online_one_img(yd_user_id) -> Union[str, bytes]:
    result = "结果↓↓↓↓↓↓\n"
    oData = await wzry_api.get_user_role(yd_user_id)
    if isinstance(oData, int):
        return get_error(oData)
    data = oData[0]
    # 获取资料数据
    profile_data = await wzry_api.get_user_profile(yd_user_id, data['roleId'])
    # roleCard
    roleCard = profile_data['roleCard']
    if roleCard['gameOnline'] == 1:
        bhd = await wzry_api.get_battle_history(yd_user_id, 10)
        if isinstance(bhd, int):
            online = '🟢在线'
        elif bhd['isGaming']:
            online = f"🟠{bhd['gaming']['mapName']}-{bhd['gaming']['title']}"
        else:
            online = '🟢在线'
    else:
        online = '⚪离线'
    result = result + (f"{roleCard['areaName']}-{roleCard['roleJobName']}\n"
                       f"\t{roleCard['roleName']} {roleCard['serverName']}\t{online}\n")
    return result
