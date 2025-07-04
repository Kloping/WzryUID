import time
from pathlib import Path
from typing import Tuple, Union
from urllib.parse import urlparse, parse_qs

from PIL import Image, ImageDraw, ImageFilter
from tomlkit.items import Array

from gsuid_core.utils.fonts.fonts import core_font
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import (
    get_color_bg,
    get_qq_avatar,
    draw_pic_with_ring,
)
from .draw_battle_history import draw_history_img
from ..utils.download import download_file
from ..utils.error_reply import get_error
from ..utils.resource_path import (
    BG_PATH,
    ICON_PATH,
    EQUIP_PATH,
    SKILL_PATH,
    AVATAR_PATH,
)
from ..utils.wzry_api import wzry_api

TEXT_PATH = Path(__file__).parent / 'texture2d'


async def draw_history_one_img(
    user_id: str, yd_user_id: str, hn: str
) -> Union[str, bytes]:
    heroId = -1
    map0 = await wzry_api.get_hero_map();
    for heroInfo in map0:
        if hn == heroInfo['cname']:
            heroId = heroInfo['ename']
            break
        else:
            continue

    if heroId == -1:
        return await draw_history_img(user_id, yd_user_id)
    oData = await wzry_api.get_user_role(yd_user_id)
    if isinstance(oData, int):
        return get_error(oData)

    data = oData[0]
    roleId = data['roleId']
    serverId = data['serverId']
    lt = round(time.time())
    history_list: Array = None
    blist: Array = None
    upblist: Array = None
    while True:
        if blist is None:
            blist = await wzry_api.get_battle_one_history(serverId, roleId, heroId, lt)
            upblist = blist
            history_list = blist['zjList']
            if len(history_list) < 5: break
        else:
            zjList = upblist['zjList']
            lt = int(zjList[len(zjList) - 1]['gameseq'])
            upblist = await wzry_api.get_battle_one_history(serverId, roleId, heroId, lt)
            history_list.extend(upblist['zjList'])
            if len(upblist['zjList']) < 5: break
        if len(history_list) >= 12: break
    ## 成功获得 指定英雄对局列表

    game_text = '未知游戏状态'

    battle_data = history_list[:12]

    if len(battle_data) < 12:
        h = 500 + len(battle_data) * 120 + 60
    else:
        h = 2000

    img = await get_color_bg(950, h, BG_PATH)
    img = img.filter(ImageFilter.GaussianBlur(28))
    avatar_img = await get_qq_avatar(avatar_url=data['roleIcon'])
    avatar_img = await draw_pic_with_ring(avatar_img, 320)

    title = Image.open(TEXT_PATH / 'title.png')
    ring = Image.open(TEXT_PATH / 'avatar_ring.png')

    img.paste(avatar_img, (310, 70), avatar_img)
    img.paste(title, (0, 405), title)
    hero_mask = Image.open(TEXT_PATH / 'avatar_mask.png')
    skill_mask = Image.open(TEXT_PATH / 'skill_mask.png')

    hero_img = None
    text_color = (48, 48, 48)
    for index, battle in enumerate(battle_data):
        is_win = True if battle['gameresult'] == "1" else False
        date = battle["gametime"]
        if is_win:
            bar_text = '胜利'
            babg = Image.open(TEXT_PATH / 'win_bg.png')
            bar_color = (66, 183, 255)
        else:
            bar_text = '失败'
            babg = Image.open(TEXT_PATH / 'lose_bg.png')
            bar_color = (255, 66, 66)

        # 解析 URL
        parsed_url = urlparse(battle['detailUrl'])

        # 获取查询参数部分
        query_params = parse_qs(parsed_url.query)

        # 将参数值从列表转换为单个值（如果只有一个值）
        params_dict = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}

        # 从链接中截取 请求对局详情必要的参数 对应账号
        detail_data = await wzry_api.get_battle_detail(
            roleId,
            params_dict['gameSvrId'],
            params_dict['relaySvrId'],
            params_dict['gameseq'],
            battle['pvptype'],
        )
        self_data = None

        hero_path = AVATAR_PATH / f'{battle["HeroID1"]}.png'
        icon_path = battle["heroIcon"]
        name_path = f'{battle["HeroID1"]}.png'

        if not isinstance(detail_data, int):
            detail_data['redRoles'].extend(detail_data['blueRoles'])
            all_roles = detail_data['redRoles']

            for ro0 in all_roles:
                if self_data is None:
                    basicInfo = ro0['basicInfo']
                    isMe = basicInfo['isMe']
                    if bool(isMe):
                        self_data = ro0

            skin0 = self_data['battleRecords']['usedSkin']

            if skin0 is not None:
                skin_id = skin0['skinId']
                hero_path = AVATAR_PATH / f'{battle["HeroID1"]}-{skin_id}.png'
                icon_path = skin0['skinIcon']
                name_path = f'{battle["HeroID1"]}-{skin0["skinId"]}.png'
            # 画召唤师技能
            battle_records = self_data['battleRecords']
            skill = battle_records['skill']
            skill_id = skill['skillId']
            skill_path = SKILL_PATH / f'{skill_id}.png'
            if not skill_path.exists():
                await download_file(
                    skill['skillIcon'], SKILL_PATH, f'{skill_id}.png'
                )
            skill_img = Image.open(skill_path)
            skill_img = skill_img.resize((45, 45))
            babg.paste(skill_img, (390, 65), skill_mask)
            # 画装备
            equips = battle_records['finalEquips']
            eix = 1
            eiy = 0
            for ei0, equip in enumerate(equips):
                equip_id = equip['equipId']
                equip_path = EQUIP_PATH / f'{equip_id}.png'
                if not equip_path.exists():
                    await download_file(
                        equip['equipIcon'], EQUIP_PATH, f'{equip_id}.png'
                    )
                equip_img = Image.open(equip_path)
                equip_img = equip_img.resize((45, 45))
                babg.paste(
                    equip_img,
                    (405 + (eix * 50), int(eiy * 50 + 15)),
                    skill_mask,
                )
                eix = eix + 1
                if eix == 4:
                    eiy = eiy + 1
                    eix = 1

        if not hero_path.exists():
            await download_file(icon_path, AVATAR_PATH, name_path)

        hero_img = Image.open(hero_path)
        if hero_img.size[0] != hero_img.size[1]:
            hero_img = hero_img.crop(
                (0, 0, hero_img.size[0], hero_img.size[0])
            )
        hero_img = hero_img.resize((100, 100))
        babg.paste(hero_img, (79, 9), hero_mask)
        babg.paste(ring, (78, 8), ring)

        babg_draw = ImageDraw.Draw(babg)

        kill = battle['killcnt']
        dead = battle['deadcnt']
        assist = battle['assistcnt']

        babg_draw.text((210, 50), bar_text, bar_color, core_font(32), 'lm')
        babg_draw.text(
            (281, 52), battle['mapName'], text_color, core_font(18), 'lm'
        )

        if battle['matchDesc'] != "":
            babg_draw.rectangle(
                (636, 10, 676, 110),
                fill=(241, 224, 198, 33),
                outline=(100, 35, 0, 56),
                width=2,
            )
            for ie0, e1 in enumerate(battle['matchDesc']):
                babg_draw.text((644, 30 + (ie0 * 30)), e1, bar_color, core_font(26), 'lm')

        babg_draw.text(
            (210, 83),
            f"{kill} / {dead} / {assist}",
            text_color,
            core_font(33),
            'lm',
        )
        babg_draw.text((855, 94), date, text_color, core_font(20), 'rm')

        if battle['evaluateUrlV3']:
            await paste_icon(battle['evaluateUrlV3'], babg, (755, 10))

        if battle['mvpUrlV3']:
            await paste_icon(battle['mvpUrlV3'], babg, (755, 45))

        img.paste(babg, (0, 540 + index * 120), babg)

    img_draw = ImageDraw.Draw(img)
    img_draw.text(
        (475, 437), '王者荣耀战绩', (10, 10, 10), core_font(40), 'mm'
    )
    img_draw.text((475, 495), game_text, text_color, core_font(30), 'mm')
    all_black = Image.new('RGBA', img.size, (255, 255, 255))
    img = Image.alpha_composite(all_black, img)

    return await convert_img(img)


async def paste_icon(url: str, img: Image.Image, pos: Tuple[int, int]):
    icon_name: str = url.split('/')[-1]
    path = ICON_PATH / icon_name
    if not path.exists():
        await download_file(url, ICON_PATH, icon_name)
    eval_icon = Image.open(path)
    eval_icon = eval_icon.resize(
        (int(eval_icon.size[0] * 0.7), int(eval_icon.size[1] * 0.7))
    )
    img.paste(eval_icon, pos, eval_icon)
