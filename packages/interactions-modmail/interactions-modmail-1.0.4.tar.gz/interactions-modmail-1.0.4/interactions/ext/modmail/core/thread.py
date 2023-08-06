import asyncio
import contextlib
import os
import re
import typing
from datetime import datetime, timedelta, timezone
from json import dump, load
from logging import getLogger

import isodate
from pytz import UTC

from interactions import (
    Channel,
    ChannelType,
    Client,
    CommandContext,
    Embed,
    Guild,
    InteractionException,
    Member,
    Message,
    MessageReaction,
    Role,
    ThreadMember,
    User,
)
from interactions.ext.get import get

from .models import DMDisabled
from .time import human_timedelta
from .utils import (
    days,
    get_joint_id,
    get_top_hoisted_role,
    match_other_recipients,
    match_title,
    match_user_id,
)

logger = getLogger("thread")


class Thread:
    """Represents a discord Modmail thread"""

    def __init__(
        self,
        manager: "ThreadManager",
        recipient: typing.Union[Member, User, int],
        channel: Channel = None,
        other_recipients: typing.List[typing.Union[Member, User]] = None,
    ):
        self.manager = manager
        self.bot: Client = manager.bot
        if isinstance(recipient, int):
            self._id = recipient
            self._recipient = None
        else:
            if recipient.bot:
                raise InteractionException(0, message="Recipient cannot be a bot.")
            self._id = recipient.id
            self._recipient = recipient
        self._other_recipients = other_recipients or []
        self._channel = channel
        self.genesis_message = None
        self._ready_event = asyncio.Event()
        self.wait_tasks = []
        self.close_task = None
        self.auto_close_task = None
        self._cancelled = False

    def __repr__(self):
        return f'Thread(recipient="{self.recipient or self.id}", channel={self.channel.id}, other_recipients={len(self._other_recipients)})'

    def __eq__(self, other):
        if isinstance(other, Thread):
            return self.id == other.id
        return super().__eq__(other)

    async def wait_until_ready(self) -> None:
        """Blocks execution until the thread is fully set up."""
        # timeout after 30 seconds
        task = asyncio.create_task(asyncio.wait_for(self._ready_event.wait(), timeout=25))
        self.wait_tasks.append(task)
        with contextlib.suppress(asyncio.TimeoutError):
            await task
        self.wait_tasks.remove(task)

    @property
    def id(self) -> int:
        return int(self._id)

    @property
    def channel(self) -> Channel:
        return self._channel

    @property
    def recipient(self) -> typing.Optional[typing.Union[User, Member]]:
        return self._recipient

    @property
    def recipients(self) -> typing.List[typing.Union[User, Member]]:
        return [self._recipient] + self._other_recipients

    @property
    def ready(self) -> bool:
        return self._ready_event.is_set()

    @ready.setter
    def ready(self, flag: bool):
        if flag:
            self._ready_event.set()
        else:
            self._ready_event.clear()

    @property
    def cancelled(self) -> bool:
        return self._cancelled

    @cancelled.setter
    def cancelled(self, flag: bool):
        self._cancelled = flag
        if flag:
            for i in self.wait_tasks:
                i.cancel()

    @classmethod
    async def from_channel(cls, manager: "ThreadManager", channel: Channel) -> "Thread":
        recipient_id = match_user_id(
            channel.name
        )  # there is a chance it grabs from another recipient's main thread

        if recipient_id in manager.cache:
            return manager.cache[recipient_id]
        recipient = await get(manager.bot, User, user_id=recipient_id)

        other_recipients = []
        for uid in match_other_recipients(channel.name):
            # try:
            other_recipient = await get(manager.bot, User, user_id=uid)
            # except discord.NotFound: # LibraryException somewhen(tm)
            #   continue
            other_recipients.append(other_recipient)

        return cls(manager, recipient, channel, other_recipients)

    async def setup(self, guild_id, *, creator=None, category: Channel = None):
        """Create the thread channel and other io related initialisation tasks"""
        recipient = self.recipient
        if recipient is None:
            self._recipient = await get(self.bot, User, user_id=self.id)
            recipient = self.recipient

        category = category or await self.manager.modmail.main_category(guild_id)
        thread_channel_id = self.manager.modmail.config["thread_channel_id"][str(category.id)]
        guild = await get(self.bot, Guild, guild_id=guild_id)
        thread_channel = await get(self.bot, Channel, channel_id=int(thread_channel_id))

        channel = await thread_channel.create_thread(
            name=f"Modmail Thread, User ID: {recipient.id}",
            auto_archive_duration=10080,
        )

        # except discord.HTTPException as e:  # Failed to create due to missing perms.
        #     logger.critical("An error occurred while creating a thread.", exc_info=True)
        #     self.manager.cache.pop(self.id)
        #
        #     embed = discord.Embed(color=self.bot.error_color)
        #     embed.title = "Error while trying to create a thread."
        #     embed.description = str(e)
        #     embed.add_field(name="Recipient", value=recipient.mention)
        #
        #     if self.bot.log_channel is not None:
        #         await self.bot.log_channel.send(embed=embed)
        #     return
        # TO BE REPLACED WITH LIB EXC
        self._channel = channel

        log_url = log_count = None

        self.ready = True

        if creator is not None and creator != recipient:
            mention = None
        else:
            mention = self.manager.modmail.config["mention"]

        async def send_genesis_message():
            info_embed = await self._format_info_embed(
                guild, recipient, log_url, log_count, self.manager.modmail.main_color
            )
            try:
                msg = await channel.send(mention, embeds=info_embed)
                await msg.pin()
                self.genesis_message = msg
            except Exception:
                logger.error("Failed unexpectedly:", exc_info=True)

        async def send_recipient_genesis_message():
            nonlocal channel
            # Once thread is ready, tell the recipient (don't send if using contact on others)
            thread_creation_response = self.manager.modmail.config["thread_creation_response"]

            embed = Embed(
                color=self.manager.modmail.mod_color,
                description=thread_creation_response,
                timestamp=channel.id.timestamp,
            )

            recipient_thread_close = self.manager.modmail.config.get("recipient_thread_close")

            if recipient_thread_close:
                footer = self.manager.modmail.config["thread_self_closable_creation_footer"]
            else:
                footer = self.manager.modmail.config["thread_creation_footer"]

            embed.set_footer(text=footer, icon_url=guild.icon_url)
            embed.title = self.manager.modmail.config["thread_creation_title"]

            if creator is None or creator == recipient:
                if isinstance(recipient, User):
                    _channel = Channel(
                        **await self.bot._http.create_dm(int(recipient.id)), _client=self.bot._http
                    )
                    msg = await _channel.send(embeds=embed)
                else:
                    msg = await recipient.send(embeds=embed)

                if recipient_thread_close:
                    close_emoji = self.manager.modmail.config["close_emoji"]
                    await msg.create_reaction(close_emoji)

        await send_genesis_message()
        await send_recipient_genesis_message()

    async def _format_info_embed(
        self, guild: Guild, user: typing.Union[Member, User], log_url, log_count, color
    ):
        """Get information about a member of a server
        supports users from the guild or not."""
        member = await guild.get_member(int(user.id)) if isinstance(user, User) else user
        time = datetime.now(tz=timezone.utc)
        role_names = ""
        if member is not None and self.manager.modmail.config["thread_show_roles"]:
            sep_server = True
            separator = ", " if sep_server else " "

            roles = []
            if not guild.roles:
                guild.roles = await guild.get_all_roles()
            _roles = [await get(guild.roles, id=_) for _ in member.roles]
            for role in sorted(_roles, key=lambda r: r.position):
                if int(role.id) == int(guild.id):
                    # @everyone
                    continue

                fmt = role.name if sep_server else role.mention
                roles.append(fmt)

                if len(separator.join(roles)) > 1024:
                    roles.append("...")
                    while len(separator.join(roles)) > 1024:
                        roles.pop(-2)
                    break

            role_names = separator.join(roles)

        user_info = []
        if self.manager.modmail.config["thread_show_account_age"]:
            timestamp = UTC.localize(user.id.timestamp)
            created = str((time - timestamp).days)
            user_info.append(f"was created {days(created)}")

        embed = Embed(color=color, description=user.mention, timestamp=time)

        footer = f"User ID: {user.id}"

        embed.set_author(name=str(user), icon_url=user.avatar_url, url=log_url)
        # embed.set_thumbnail(url=avi)

        if member is not None:
            # embed.add_field(name='Joined', value=joined + days(joined))
            if self.manager.modmail.config["thread_show_join_age"]:
                joined = str((time - member.joined_at).days)
                user_info.append(f"joined {days(joined)}")

            if member.nick:
                embed.add_field(name="Nickname", value=member.nick, inline=True)
            if role_names:
                embed.add_field(name="Roles", value=role_names, inline=True)
            embed.set_footer(text=footer)
        else:
            embed.set_footer(text=f"{footer} • (not in main server)")

        embed.description += ", ".join(user_info)

        if log_count is not None:
            connector = "with" if user_info else "has"
            thread = "thread" if log_count == 1 else "threads"
            embed.description += f" {connector} **{log_count or 'no'}** past {thread}."
        else:
            embed.description += "."

        return embed

    def _close_after(self, closer, silent, delete_channel, message):
        return self.bot._loop.create_task(
            self._close(closer, silent, delete_channel, message, True)
        )

    async def close(
        self,
        *,
        closer: typing.Union[Member, User],
        after: int = 0,
        silent: bool = False,
        delete_channel: bool = True,
        message: str = None,
        auto_close: bool = False,
    ) -> None:
        """Close a thread now or after a set time in seconds"""

        # restarts the after timer
        await self.cancel_closure(auto_close)

        if after > 0:
            # TODO: Add somewhere to clean up broken closures
            #  (when channel is already deleted)
            now = datetime.now(timezone.utc)
            items = {
                # 'initiation_time': now.isoformat(),
                "time": (now + timedelta(seconds=after)).isoformat(),
                "closer_id": closer.id,
                "silent": silent,
                "delete_channel": delete_channel,
                "message": message,
                "auto_close": auto_close,
            }
            self.manager.modmail.config["closures"][str(self.id)] = items
            path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")
            with open(f"{path}/config.json", "r+") as cfg:
                _cfg = load(cfg)
                _cfg["closures"] = self.manager.modmail.config["closures"]
                cfg.truncate(0)
                cfg.seek(0)
                dump(_cfg, cfg)
            task = self.bot._loop.call_later(
                after, self._close_after, closer, silent, delete_channel, message
            )

            if auto_close:
                self.auto_close_task = task
            else:
                self.close_task = task
        else:
            await self._close(closer, silent, delete_channel, message)

    async def _close(
        self, closer, silent=False, delete_channel=True, message=None, scheduled=False
    ):
        try:
            self.manager.cache.pop(self.id)
        except KeyError as e:
            logger.error("Thread already closed: %s.", e)
            return

        await self.cancel_closure(all=True)

        # Cancel auto closing the thread if closed by any means.

        self.manager.modmail.config["subscriptions"].pop(str(self.id), None)
        self.manager.modmail.config["notification_squad"].pop(str(self.id), None)

        desc = "Could not resolve log url."
        log_url = None

        embed = Embed(description=desc, color=self.manager.modmail.error_color)

        if self.recipient is not None:
            user = f"{self.recipient} (`{self.id}`)"
        else:
            user = f"`{self.id}`"

        if self.id == closer.id:
            _closer = "the Recipient"
        else:
            _closer = f"{closer} ({closer.id})"

        embed.title = user

        event = "Thread Closed as Scheduled" if scheduled else "Thread Closed"
        # embed.set_author(name=f"Event: {event}", url=log_url)
        embed.set_footer(text=f"{event} by {_closer}", icon_url=closer.user.avatar_url)
        embed.timestamp = datetime.now(timezone.utc)

        tasks = []

        # Thread closed message

        embed = Embed(
            title=self.manager.modmail.config["thread_close_title"],
            color=self.manager.modmail.error_color,
        )
        if self.manager.modmail.config["show_timestamp"]:
            embed.timestamp = datetime.now(timezone.utc)

        if not message:
            if self.id == closer.id:
                message = self.manager.modmail.config["thread_self_close_response"]
            else:
                message = self.manager.modmail.config["thread_close_response"]

        message = self.manager.modmail.formatter.format(message, closer=closer, loglink=log_url)

        embed.description = message
        footer = self.manager.modmail.config["thread_close_footer"]
        embed.set_footer(text=footer)

        if not silent:
            for user in self.recipients:
                if not message:
                    if user.id == closer.id:
                        message = self.manager.modmail.config["thread_self_close_response"]
                    else:
                        message = self.manager.modmail.config["thread_close_response"]
                    embed.description = message

                if user is not None:
                    if isinstance(user, User):
                        _channel = Channel(
                            **await self.bot._http.create_dm(int(user.id)), _client=self.bot._http
                        )
                        await _channel.send(embeds=embed)
                        tasks.append(_channel.send(embeds=embed))
                    else:
                        tasks.append(user.send(embeds=embed))

        if delete_channel:
            tasks.append(
                self.channel.modify(
                    archived=True,
                    locked=True,
                    permission_overwrites=[],
                    reason="Closing modmail thread",
                )
            )

        await asyncio.gather(*tasks)

    async def cancel_closure(self, auto_close: bool = False, all: bool = False) -> None:
        if self.close_task is not None and (not auto_close or all):
            self.close_task.cancel()
            self.close_task = None
        if self.auto_close_task is not None and (auto_close or all):
            self.auto_close_task.cancel()
            self.auto_close_task = None

        to_update = self.manager.modmail.config["closures"].pop(str(self.id), None)
        if to_update is not None:
            path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")
            with open(f"{path}/config.json", "r+") as cfg:
                _cfg = load(cfg)
                _cfg["closures"] = self.manager.modmail.config["closures"]
                cfg.truncate(0)
                cfg.seek(0)
                dump(_cfg, cfg)

    async def _restart_close_timer(self):
        """
        This will create or restart a timer to automatically close this
        thread.
        """
        timeout = self.manager.modmail.config.get("thread_auto_close")

        # Exit if timeout was not set
        if timeout == isodate.Duration():
            return

        # Set timeout seconds
        seconds = timeout.total_seconds()
        # seconds = 20  # Uncomment to debug with just 20 seconds
        reset_time = datetime.now(timezone.utc) + timedelta(seconds=seconds)
        human_time = human_timedelta(dt=reset_time)

        if self.manager.modmail.config.get("thread_auto_close_silently"):
            return await self.close(
                closer=await get(self.bot, User, user_id=int(self.bot.me.id)),
                silent=True,
                after=int(seconds),
                auto_close=True,
            )

        # Grab message
        close_message = self.manager.modmail.formatter.format(
            self.manager.modmail.config["thread_auto_close_response"], timeout=human_time
        )

        time_marker_regex = "%t"
        if len(re.findall(time_marker_regex, close_message)) == 1:
            close_message = re.sub(time_marker_regex, str(human_time), close_message)
        elif len(re.findall(time_marker_regex, close_message)) > 1:
            logger.warning(
                "The thread_auto_close_response should only contain one '%s' to specify time.",
                time_marker_regex,
            )

        await self.close(
            closer=await get(self.bot, User, user_id=int(self.bot.me.id)),
            after=int(seconds),
            message=close_message,
            auto_close=True,
        )

    async def find_linked_messages(
        self,
        message_id: typing.Optional[int] = None,
        either_direction: bool = False,
        message1: Message = None,
        note: bool = True,
    ) -> typing.Tuple[Message, typing.List[typing.Optional[Message]]]:
        if message1 is not None:
            if (
                not message1.embeds
                or not message1.embeds[0].author.url
                or message1.author != await get(self.bot, User, user_id=int(self.bot.me.id))
            ):
                raise ValueError("Malformed thread message.")

        elif message_id is not None:
            # try:
            #     message1 = await self.channel.fetch_message(message_id)
            # except discord.NotFound:
            #     raise ValueError("Thread message not found.")

            if not (
                message1.embeds
                and message1.embeds[0].author.url
                and message1.embeds[0].color
                and message1.author.bot
            ):
                raise ValueError("Thread message not found.")

            if message1.embeds[0].color == self.manager.modmail.main_color and (
                message1.embeds[0].author.name.startswith("Note")
                or message1.embeds[0].author.name.startswith("Persistent Note")
            ):
                if not note:
                    raise ValueError("Thread message not found.")
                return message1, None

            if message1.embeds[0].color.value != self.manager.modmail.mod_color and not (
                either_direction
                and message1.embeds[0].color == self.manager.modmail.recipient_color
            ):
                raise ValueError("Thread message not found.")
        else:
            for message1 in await self.channel.get_history(limit=200):
                if (
                    message1.embeds
                    and message1.embeds[0].author.url
                    and message1.embeds[0].color
                    and (
                        message1.embeds[0].color == self.manager.modmail.mod_color
                        or (
                            either_direction
                            and message1.embeds[0].color == self.manager.modmail.recipient_color
                        )
                    )
                    and message1.embeds[0].author.url.split("#")[-1].isdigit()
                    and message1.author.bot
                ):
                    break
            else:
                raise ValueError("Thread message not found.")

        try:
            joint_id = int(message1.embeds[0].author.url.split("#")[-1])
        except ValueError as e:
            raise ValueError("Malformed thread message.") from e

        messages = [message1]
        for user in self.recipients:
            dm_channel = Channel(
                **await self.bot._http.create_dm(int(user.id)), _client=self.bot._http
            )
            for msg in await dm_channel.get_history(200):
                if either_direction and msg.id == joint_id:
                    return message1, msg

                if not (msg.embeds and msg.embeds[0].author.url):
                    continue
                try:
                    if int(msg.embeds[0].author.url.split("#")[-1]) == joint_id:
                        messages.append(msg)
                        break
                except ValueError:
                    continue

        if len(messages) > 1:
            return messages

        raise ValueError("DM message not found.")

    async def edit_message(self, message_id: typing.Optional[int], message: str) -> None:
        try:
            message1, *message2 = await self.find_linked_messages(message_id)
        except ValueError:
            logger.warning("Failed to edit message.", exc_info=True)
            raise

        embed1 = message1.embeds[0]
        embed1.description = message

        tasks = [message1.edit(embeds=embed1)]
        if message2 is not [None]:
            for m2 in message2:
                embed2 = m2.embeds[0]
                embed2.description = message
                tasks += [m2.edit(embeds=embed2)]

        await asyncio.gather(*tasks)

    async def delete_message(
        self, message: typing.Union[int, Message] = None, note: bool = True
    ) -> None:
        if isinstance(message, Message):
            message1, *message2 = await self.find_linked_messages(message1=message, note=note)
        else:
            message1, *message2 = await self.find_linked_messages(message, note=note)
        tasks = []

        if not isinstance(message, Message):
            tasks += [message1.delete()]

        for m2 in message2:
            if m2 is not None:
                tasks += [m2.delete()]

        if tasks:
            await asyncio.gather(*tasks)

    async def find_linked_message_from_dm(
        self, message: Message, either_direction=False, get_thread_channel=False
    ) -> typing.List[Message]:

        joint_id = get_joint_id(message) if either_direction else None
        linked_messages = []
        if self.channel is None:
            raise ValueError("Thread channel message not found.")
        for msg in await self.channel.get_history(200):
            if not msg.embeds:
                continue

            msg_joint_id = get_joint_id(msg)
            if msg_joint_id is None:
                continue

            if msg_joint_id == message.id:
                linked_messages.append(msg)
                break

            if joint_id is not None and msg_joint_id == joint_id:
                linked_messages.append(msg)
                break
        else:
            raise ValueError("Thread channel message not found.")
        if get_thread_channel:
            # end early as we only want the main message from thread channel
            return linked_messages

        if joint_id is None:
            joint_id = get_joint_id(linked_messages[0])
        if joint_id is None:
            # still None, supress this and return the thread message
            logger.error("Malformed thread message.")
            return linked_messages

        msg_channel = await message.get_channel()
        for user in self.recipients:
            if (
                dm_channel := Channel(
                    **await self.bot._http.create_dm(int(user.id)), _client=self.bot._http
                )
            ) == msg_channel:
                continue
            for other_msg in await dm_channel.get_history(200):
                if either_direction and other_msg.id == joint_id:
                    linked_messages.append(other_msg)
                    break

                if not other_msg.embeds:
                    continue

                other_joint_id = get_joint_id(other_msg)
                if other_joint_id is not None and other_joint_id == joint_id:
                    linked_messages.append(other_msg)
                    break
            else:
                logger.error("Linked message from recipient %s not found.", user)

        return linked_messages

    async def edit_dm_message(self, message: Message, content: str) -> None:
        try:
            linked_messages = await self.find_linked_message_from_dm(message)
        except ValueError:
            logger.warning("Failed to edit message.", exc_info=True)
            raise

        for msg in linked_messages:
            embed = msg.embeds[0]
            ch = await message.get_channel()
            if ch.type != ChannelType.DM:
                # just for thread channel, we put the old message in embed field
                embed.add_field(name="**Edited, former message:**", value=embed.description)
            embed.description = content
            await msg.edit(embeds=embed)

    async def reply(
        self, ctx: CommandContext, message: str, anonymous: bool = False, plain: bool = False
    ) -> typing.Tuple[Message, Message]:

        tasks = []

        user_msg_tasks = [
            self.send(
                ctx,
                message,
                destination=user,
                from_mod=True,
                anonymous=anonymous,
                plain=plain,
            )
            for user in self.recipients
        ]

        try:
            await asyncio.gather(*user_msg_tasks)
        except Exception:
            logger.error("Message delivery failed:", exc_info=True)
            # if isinstance(e, discord.Forbidden):
            #     description = (
            #         "Your message could not be delivered as "
            #         "the recipient is only accepting direct "
            #         "messages from friends, or the bot was "
            #         "blocked by the recipient."
            #     )
            # else:
            description = "Your message could not be delivered due " "to an unknown error."
            await ctx.get_channel()
            tasks.append(
                ctx.channel.send(
                    embeds=Embed(
                        color=self.manager.modmail.error_color,
                        description=description,
                    )
                )
            )
        else:
            # Send the same thing in the thread channel.
            await self.send(
                ctx,
                message,
                destination=self.channel,
                from_mod=True,
                anonymous=anonymous,
                plain=plain,
            )

            # Cancel closing if a thread message is sent.
            if self.close_task is not None:
                await self.cancel_closure()
                tasks.append(
                    self.channel.send(
                        embeds=Embed(
                            color=self.manager.modmail.error_color,
                            description="Scheduled close has been cancelled.",
                        )
                    )
                )

        await asyncio.gather(*tasks)

    async def send(
        self,
        ctx: typing.Union[CommandContext, Message],
        message: str,
        destination: typing.Union[Channel, User, Member] = None,
        from_mod: bool = False,
        note: bool = False,
        anonymous: bool = False,
        plain: bool = False,
        persistent_note: bool = False,
    ) -> None:

        if not note and from_mod:
            self.bot._loop.create_task(
                self._restart_close_timer()
            )  # Start or restart thread auto close

        if self.close_task is not None:
            # cancel closing if a thread message is sent.
            self.bot._loop.create_task(self.cancel_closure())
            await self.channel.send(
                embeds=Embed(
                    color=self.manager.modmail.error_color,
                    description="Scheduled close has been cancelled.",
                )
            )

        if not self.ready:
            await self.wait_until_ready()

        destination = destination or self.channel

        author: Member = ctx.author if isinstance(ctx, CommandContext) else ctx.member
        guild = await ctx.get_guild()

        embed = Embed(description=message)
        if self.manager.modmail.config["show_timestamp"]:
            embed.timestamp = ctx.id.timestamp

        if note:
            system_avatar_url = "https://discordapp.com/assets/f78426a064bc9dd24847519259bc42af.png"

            # Special note messages
            embed.set_author(
                name=f"{'Persistent' if persistent_note else ''} Note ({author.name})",
                icon_url=system_avatar_url,
            )

        elif (
            anonymous
            and from_mod
            and (not isinstance(destination, Channel) or destination.type == ChannelType.DM)
        ):
            # Anonymously sending to the user.
            tag = self.manager.modmail.config["mod_tag"]
            if tag is None:
                tag = await get_top_hoisted_role(guild, author)
            name = self.manager.modmail.config["anon_username"]
            if name is None:
                name = tag.name
            avatar_url = self.manager.modmail.config["anon_avatar_url"]
            if avatar_url is None:
                avatar_url = guild.icon_url
            embed.set_author(
                name=name,
                icon_url=avatar_url,
            )
        else:
            # Normal message
            name = str(author)
            avatar_url = author.user.avatar_url
            embed.set_author(
                name=name,
                icon_url=avatar_url,
            )

        if from_mod:
            # Anonymous reply sent in thread channel
            if anonymous and (
                isinstance(destination, Channel) and destination.type == ChannelType.DM
            ):
                embed.set_footer(text="Anonymous Reply")
            # Normal messages
            elif not anonymous:
                mod_tag = self.manager.modmail.config["mod_tag"]
                if mod_tag is None:
                    mod_tag: Role = await get_top_hoisted_role(guild, author)
                embed.set_footer(text=mod_tag.name)  # Normal messages
            else:
                embed.set_footer(text=self.manager.modmail.config["anon_tag"])

            if (
                self.manager.modmail.config["dm_disabled"] == DMDisabled.ALL_THREADS
                and destination != self.channel
            ):
                logger.info("Sending a message to %s when DM disabled is set.", self.recipient)

        # try:
        await self.bot._http.trigger_typing(int(destination.id)) if isinstance(
            destination, Channel
        ) else None
        # except discord.NotFound:
        #   logger.warning("Channel not found.")
        #   raise

        mentions = self.get_notifications() if not from_mod and not note else None
        if plain:
            if from_mod and not (
                isinstance(destination, Channel) and destination.type == ChannelType.DM
            ):
                # Plain to user
                plain_message = f"**({embed.footer.text}) " if embed.footer.text else "**"
                plain_message += f"{embed.author.name}:** {embed.description}"

                msg = await destination.send(plain_message)
            else:
                # Plain to mods
                embed.set_footer(text=f"[PLAIN] {embed.footer.text}")
                msg = await destination.send(mentions, embeds=embed)

        elif isinstance(destination, User):
            _channel = Channel(
                **await self.bot._http.create_dm(int(destination.id)), _client=self.bot._http
            )
            msg = await _channel.send(embeds=embed)
        else:
            msg = await destination.send(mentions, embeds=embed)

        return msg

    def get_notifications(self) -> str:
        key = str(self.id)

        mentions = []
        mentions.extend(self.manager.modmail.config["subscriptions"].get(key, []))

        if key in self.manager.modmail.config["notification_squad"]:
            mentions.extend(self.manager.modmail.config["notification_squad"][key])
            self.manager.modmail.config["notification_squad"].pop(key)

        return " ".join(set(mentions))

    async def set_title(self, title: str) -> None:
        user_id = match_user_id(self.channel.name)
        ids = ",".join(str(i.id) for i in self._other_recipients)

        await self.channel.modify(
            name=f"Title: {title}, User ID: {user_id}, Other Recipients: {ids}",
            permission_overwrites=[],
        )

    async def add_users(self, users: typing.List[typing.Union[Member, User]]) -> None:
        title = match_title(self.channel.name)
        user_id = match_user_id(self.channel.name)
        self._other_recipients += users

        ids = ",".join(str(i.id) for i in self._other_recipients)
        await self.channel.modify(
            name=f"Title: {title}, User ID: {user_id}, Other Recipients: {ids}",
            permission_overwrites=[],
        )

    async def remove_users(self, users: typing.List[typing.Union[Member, User]]) -> None:
        title = match_title(self.channel.name)
        user_id = match_user_id(self.channel.name)
        for u in users:
            for elem in self._other_recipients:
                if int(elem.id) == int(u.id):
                    self._other_recipients.remove(elem)

        ids = ",".join(str(i.id) for i in self._other_recipients)
        await self.channel.modify(
            name=f"Title: {title}, User ID: {user_id}, Other Recipients: {ids if ids else 'None'}",
            permission_overwrites=[],
        )


class ThreadManager:
    """Class that handles storing, finding and creating Modmail threads."""

    def __init__(self, bot, modmail):
        self.bot: Client = bot
        self.modmail = modmail
        self.cache = {}

    async def populate_cache(self) -> None:
        for _id in self.modmail.config.get("modmail_guild_id"):
            guild = self.modmail.modmail_guild(_id)
            res = await self.bot._http.list_active_threads(int(guild.id))
            threads = [Channel(**thread, _client=self.bot._http) for thread in res["threads"]]
            members = [ThreadMember(**member, _client=self.bot._http) for member in res["members"]]
            for member in members:
                for thread in threads:
                    if int(thread.id) == int(member.id):
                        thread.member = member
                        break
            guild.threads = threads
            for channel in guild.threads:
                await self.find(channel=channel)

    def __len__(self):
        return len(self.cache)

    def __iter__(self):
        return iter(self.cache.values())

    def __getitem__(self, item: str) -> Thread:
        return self.cache[item]

    async def find(
        self,
        *,
        recipient: typing.Union[Member, User] = None,
        channel: Channel = None,
        recipient_id: int = None,
    ) -> typing.Optional[Thread]:
        """Finds a thread from cache or from discord channel topics."""
        if recipient is None and channel is not None:
            thread = await self._find_from_channel(channel)
            if thread is None:
                user_id, thread = next(
                    ((k, v) for k, v in self.cache.items() if v.channel == channel), (-1, None)
                )
                if thread is not None:
                    logger.debug("Found thread with tempered ID.")
                    await channel.modify(topic=f"User ID: {user_id}", permission_overwrites=[])
            return thread

        if recipient:
            recipient_id = recipient.id

        thread = self.cache.get(recipient_id)
        if thread is not None:
            try:
                await thread.wait_until_ready()
            except asyncio.CancelledError:
                logger.warning("Thread for %s cancelled.", recipient)
                return thread
            else:
                if not thread.cancelled and (
                    not thread.channel
                    or not await get(self.bot, Channel, channel_id=int(thread.channel.id))
                ):
                    logger.warning(
                        "Found existing thread for %s but the channel is invalid.", recipient_id
                    )
                    await thread.close(
                        closer=User(**await self.bot._http.get_self()),
                        silent=True,
                        delete_channel=False,
                    )
                    thread = None
        else:
            guilds = [
                self.modmail.modmail_guild(guild_id)
                for guild_id in self.modmail.config["modmail_guild_id"]
            ]

            for guild in guilds:
                res = await self.bot._http.list_active_threads(int(guild.id))
                threads = [Channel(**thread, _client=self.bot._http) for thread in res["threads"]]
                members = [
                    ThreadMember(**member, _client=self.bot._http) for member in res["members"]
                ]
                for member in members:
                    for _thread in threads:
                        if int(_thread.id) == int(member.id):
                            _thread.member = member
                            break
                guild.threads = threads
                channel = next(
                    (channel for channel in guild.threads if str(recipient_id) in channel.name),
                    None,
                )

            if channel:
                thread = await Thread.from_channel(self, channel)
                if thread.recipient:
                    # only save if data is valid
                    self.cache[recipient_id] = thread
                thread.ready = True

            if not channel:
                return None

        if thread and recipient_id not in [x.id for x in thread.recipients]:
            self.cache.pop(recipient_id)
            thread = None

        return thread

    async def _find_from_channel(self, channel):
        """
        Tries to find a thread from a channel channel topic,
        if channel topic doesnt exist for some reason, falls back to
        searching channel history for genesis embed and
        extracts user_id from that.
        """
        user_id = match_user_id(channel.name) if channel.name else -1
        if user_id == -1:
            return None

        if user_id in self.cache:
            return self.cache[user_id]

        # try:
        recipient = await get(self.bot, User, user_id=user_id)
        # except discord.NotFound:
        #     recipient = None

        other_recipients = []
        for uid in match_other_recipients(channel.name):
            # try:
            other_recipient = await get(self.bot, User, user_id=uid)
            # except discord.NotFound:
            #    continue
            other_recipients.append(other_recipient)

        if recipient is None:
            thread = Thread(self, user_id, channel, other_recipients)
        else:
            self.cache[user_id] = thread = Thread(self, recipient, channel, other_recipients)
        thread.ready = True

        return thread

    async def create(
        self,
        recipient: typing.Union[Member, User],
        *,
        message: Message = None,
        creator: typing.Union[Member, User] = None,
        category: Channel = None,
        manual_trigger: bool = True,
        guild_id: int = None,
    ) -> Thread:
        """Creates a Modmail thread"""

        # checks for existing thread in cache
        thread = self.cache.get(recipient.id)
        if thread:
            try:
                await thread.wait_until_ready()
            except asyncio.CancelledError:
                logger.warning("Thread for %s cancelled, abort creating.", recipient)
                return thread
            else:
                if thread.channel and await get(self.bot, Channel, channel_id=thread.channel.id):
                    logger.warning("Found an existing thread for %s, abort creating.", recipient)
                    return thread
                logger.warning(
                    "Found an existing thread for %s, closing previous thread.", recipient
                )
                await thread.close(
                    closer=User(**await self.bot._http.get_self()),
                    silent=True,
                    delete_channel=False,
                )

        thread = Thread(self, recipient)

        self.cache[recipient.id] = thread

        if (message or not manual_trigger) and self.modmail.config["confirm_thread_creation"]:
            if not manual_trigger:
                destination = recipient
            else:
                destination = await message.get_channel()
            confirm = await destination.send(
                embeds=Embed(
                    title=self.modmail.config["confirm_thread_creation_title"],
                    description=self.modmail.config["confirm_thread_response"],
                    color=self.modmail.main_color,
                )
            )
            accept_emoji = self.modmail.config["confirm_thread_creation_accept"]
            deny_emoji = self.modmail.config["confirm_thread_creation_deny"]
            emojis = [accept_emoji, deny_emoji]
            for emoji in emojis:
                await confirm.create_reaction(emoji)
                await asyncio.sleep(0.2)

            try:
                r: MessageReaction = await self.bot.wait_for(
                    "on_message_reaction_add",
                    check=lambda r: r.user_id == recipient.id
                    and r.message_id == confirm.id
                    and r.channel_id == confirm.channel_id,
                    timeout=20,
                )
            except asyncio.TimeoutError:
                thread.cancelled = True
                await destination.send(
                    embeds=Embed(
                        title=self.modmail.config["thread_cancelled"],
                        description="Timed out",
                        color=self.modmail.error_color,
                    )
                )
            else:
                deny_emoji: str
                if str(r.emoji.name.replace(":", "")) == deny_emoji.replace(":", ""):
                    thread.cancelled = True
                    await destination.send(
                        embeds=Embed(
                            title=self.modmail.config["thread_cancelled"],
                            color=self.modmail.error_color,
                        )
                    )

            async def remove_reactions():
                for emoji in emojis:
                    await confirm.remove_own_reaction_of(emoji)
                    await asyncio.sleep(0.2)

            await remove_reactions()
            if thread.cancelled:
                del self.cache[recipient.id]
                return thread

        await thread.setup(guild_id=guild_id, creator=creator, category=category)

        return thread

    async def find_or_create(self, recipient) -> Thread:
        return await self.find(recipient=recipient) or await self.create(recipient)
