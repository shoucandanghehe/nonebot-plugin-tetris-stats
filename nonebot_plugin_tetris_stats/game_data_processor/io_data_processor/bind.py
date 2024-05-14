from hashlib import md5
from urllib.parse import urlunparse

from nonebot.adapters import Bot, Event
from nonebot_plugin_alconna.uniseg import UniMessage
from nonebot_plugin_orm import get_session
from nonebot_plugin_userinfo import BotUserInfo, UserInfo  # type: ignore[import-untyped]

from ...db import BindStatus, create_or_update_bind
from ...utils.avatar import get_avatar
from ...utils.host import HostPage, get_self_netloc
from ...utils.platform import get_platform
from ...utils.render import Bind, render
from ...utils.render.schemas.base import Avatar, People
from ...utils.screenshot import screenshot
from . import alc
from .api import Player
from .constant import GAME_TYPE


@alc.assign('bind')
async def _(bot: Bot, event: Event, account: Player, bot_info: UserInfo = BotUserInfo()):  # noqa: B008
    user = await account.user
    async with get_session() as session:
        bind_status = await create_or_update_bind(
            session=session,
            chat_platform=get_platform(bot),
            chat_account=event.get_user_id(),
            game_platform=GAME_TYPE,
            game_account=user.unique_identifier,
        )
        user_info = await account.get_info()
        if bind_status in (BindStatus.SUCCESS, BindStatus.UPDATE):
            async with HostPage(
                await render(
                    'binding',
                    Bind(
                        platform='TETR.IO',
                        status='unknown',
                        user=People(
                            avatar=f'https://tetr.io/user-content/avatars/{user_info.data.user.id}.jpg?rv={user_info.data.user.avatar_revision}'
                            if user_info.data.user.avatar_revision is not None
                            else Avatar(type='identicon', hash=md5(user_info.data.user.id.encode()).hexdigest()),  # noqa: S324
                            name=user_info.data.user.username.upper(),
                        ),
                        bot=People(
                            avatar=await get_avatar(bot_info, 'Data URI', '../../static/logo/logo.svg'),
                            name=bot_info.user_name,
                        ),
                        command='io查我',
                    ),
                )
            ) as page_hash:
                await UniMessage.image(
                    raw=await screenshot(urlunparse(('http', get_self_netloc(), f'/host/{page_hash}.html', '', '', '')))
                ).finish()