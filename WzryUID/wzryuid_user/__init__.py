from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV
from gsuid_core.utils.database.api import get_uid
from gsuid_core.utils.message import send_diff_msg
from .deal_ck import deal_wz_ck, delete_wz_ck
from ..utils.database.models import WzryBind
from ..utils.error_reply import get_error
from ..utils.wzry_api import wzry_api

wzry_user_info = SV("王者用户绑定")
wzry_cookie_add = SV("王者CK添加", area="DIRECT")
wzry_cookie_delete = SV("王者CK删除", area="DIRECT", pm=0)
sv_wzry_current_uid = SV("当前绑定uid")


@wzry_user_info.on_command(
    (
        "王者绑定uid",
        "王者绑定UID",
        "王者绑定",
        "王者切换uid",
        "王者切换UID",
        "王者切换",
        "王者删除uid",
        "王者删除UID",
    ),
    block=True,
)
async def send_wz_link_uid_msg(bot: Bot, ev: Event):
    await bot.logger.info("[wzry] 开始执行[绑定/解绑用户信息]")
    qid = ev.user_id
    await bot.logger.info("[wzry] [绑定/解绑]UserID: {}".format(qid))

    uid = ev.text.strip()
    if uid and not uid.isdigit():
        return await bot.send("[wzry] 你输入了错误的格式!")

    if "绑定" in ev.command:
        data = await WzryBind.insert_uid(qid, ev.bot_id, uid, ev.group_id)
        return await send_diff_msg(
            bot,
            data,
            {
                0: f"[wzry] 绑定UID{uid}成功！",
                -1: f"[wzry] UID{uid}的位数不正确！",
                -2: f"[wzry] UID{uid}已经绑定过了！",
                -3: "[wzry] 你输入了错误的格式!",
            },
        )
    elif "切换" in ev.command:
        retcode = await WzryBind.switch_uid_by_game(qid, ev.bot_id, uid)
        if retcode == 0:
            resu = f"[wzry] 切换UID{uid}成功！"
            currentu = await WzryBind.get_uid_by_game(qid, ev.bot_id)
            resu = resu + f'/当前:{currentu}'
            allu = await WzryBind.get_uid_list_by_game(qid, ev.bot_id)
            for uuid in allu:
                oData = await wzry_api.get_user_role(uuid)
                if isinstance(oData, int) or len(oData) == 0:
                    continue
                data = oData[0]
                profile_data = await wzry_api.get_user_profile(uuid, data['roleId'])
                roleCard = profile_data['roleCard']
                resu = resu + f"\n{uuid}: {roleCard['areaName']}-{roleCard['serverName']}\n\t {roleCard['roleName']} {roleCard['roleJobName']}"
            return await bot.send(resu)
        else:
            return await bot.send(f"[wzry] 尚未绑定该UID{uid}")
    else:
        data = await WzryBind.delete_uid(qid, ev.bot_id, uid)
        return await send_diff_msg(
            bot,
            data,
            {
                0: f"[wzry] 删除UID{uid}成功！",
                -1: f"[wzry] 该UID{uid}不在已绑定列表中！",
            },
        )


@wzry_cookie_add.on_prefix(("王者添加ck", "王者添加CK"))
async def send_wz_add_ck_msg(bot: Bot, ev: Event):
    im = await deal_wz_ck(ev.bot_id, ev.text, ev.user_id)
    await bot.send(im)


@wzry_cookie_delete.on_prefix(("王者删除ck", "王者删除CK"))
async def send_wz_delete_ck_msg(bot: Bot, ev: Event):
    uid = ev.text.strip()
    if not uid or len(uid) <= 4:
        return await bot.send('末尾需要跟正确的UID, 例如 王者删除ck1234567')
    im = await delete_wz_ck(uid)
    await bot.send(im)


@sv_wzry_current_uid.on_command(('王者uid', '王者UID'))
async def send_wzry_online_list(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev, WzryBind)
    if uid is None:
        return await bot.send(get_error(-41))
    oData = await wzry_api.get_user_role(uid)
    resu = f"当前uid:{uid}"
    if isinstance(oData, int) or len(oData) != 0:
        data = oData[0]
        profile_data = await wzry_api.get_user_profile(uid, data['roleId'])
        roleCard = profile_data['roleCard']
        resu = resu + f"\n{roleCard['areaName']}-{roleCard['serverName']}\n\t {roleCard['roleName']} {roleCard['roleJobName']}"
    await bot.send(resu)
