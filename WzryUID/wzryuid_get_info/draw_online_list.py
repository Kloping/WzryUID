from pathlib import Path
from typing import Union
import numpy as np

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
        # areaName
        # "roleJobName": "尊贵铂金I",
        # "roleName": "拾;枝",
        # "serverName": "手Q30区",
        # gameOnline
        roleCard = profile_data['roleCard']
        online = '在线🟢' if roleCard['gameOnline'] == 1 else '离线🔘'
        result = result + (f"{roleCard['areaName']}-{roleCard['roleJobName']}\n"
                           f"  \t{roleCard['roleName']} {roleCard['serverName']} {online}\n")
    return result
