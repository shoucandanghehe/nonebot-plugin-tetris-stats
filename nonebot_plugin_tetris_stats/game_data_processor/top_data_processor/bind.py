from urllib.parse import urlunparse

from nonebot.adapters import Bot
from nonebot_plugin_alconna.uniseg import UniMessage
from nonebot_plugin_orm import get_session
from nonebot_plugin_userinfo import BotUserInfo, EventUserInfo, UserInfo  # type: ignore[import-untyped]

from ...db import BindStatus, create_or_update_bind
from ...utils.avatar import get_avatar
from ...utils.host import HostPage, get_self_netloc
from ...utils.platform import get_platform
from ...utils.render import Bind, render
from ...utils.render.schemas.base import People
from ...utils.screenshot import screenshot
from . import alc
from .api import Player
from .constant import GAME_TYPE


@alc.assign('bind')
async def _(
    bot: Bot,
    account: Player,
    bot_info: UserInfo = BotUserInfo(),  # noqa: B008
    event_user_info: UserInfo = EventUserInfo(),  # noqa: B008
):
    user = await account.user
    async with get_session() as session:
        bind_status = await create_or_update_bind(
            session=session,
            chat_platform=get_platform(bot),
            chat_account=event_user_info.user_id,
            game_platform=GAME_TYPE,
            game_account=user.unique_identifier,
        )
    if bind_status in (BindStatus.SUCCESS, BindStatus.UPDATE):
        async with HostPage(
            await render(
                'binding',
                Bind(
                    platform=GAME_TYPE,
                    status='unknown',
                    user=People(
                        avatar=await get_avatar(event_user_info, 'Data URI', None),
                        name=user.user_name,
                    ),
                    bot=People(
                        avatar=await get_avatar(bot_info, 'Data URI', '../../static/logo/logo.svg'),
                        name=bot_info.user_name,
                    ),
                    command='top查我',
                ),
            )
        ) as page_hash:
            await UniMessage.image(
                raw=await screenshot(urlunparse(('http', get_self_netloc(), f'/host/{page_hash}.html', '', '', '')))
            ).finish()
