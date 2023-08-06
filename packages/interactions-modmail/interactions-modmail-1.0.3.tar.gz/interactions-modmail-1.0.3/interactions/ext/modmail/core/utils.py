import base64
import contextlib
import functools
import re
import typing
from difflib import get_close_matches
from distutils.util import strtobool as _stb  # pylint: disable=import-error
from itertools import takewhile, zip_longest

from interactions import CommandContext, Embed, Guild, Member, Message, Role
from interactions.ext.get import get

__all__ = [
    "strtobool",
    "truncate",
    "format_preview",
    "days",
    "cleanup_code",
    "match_title",
    "match_user_id",
    "match_other_recipients",
    "create_not_found_embed",
    "parse_alias",
    "normalize_alias",
    "format_description",
    "trigger_typing",
    "escape_code_block",
    "tryint",
    "get_top_hoisted_role",
    "get_joint_id",
]


def strtobool(val):
    if isinstance(val, bool):
        return val
    try:
        return _stb(str(val))
    except ValueError:
        val = val.lower()
        if val == "enable":
            return 1
        if val == "disable":
            return 0
        raise


def truncate(text: str, max: int = 50) -> str:  # pylint: disable=redefined-builtin
    """
    Reduces the string to `max` length, by trimming the message into "...".

    Parameters
    ----------
    text : str
        The text to trim.
    max : int, optional
        The max length of the text.
        Defaults to 50.

    Returns
    -------
    str
        The truncated text.
    """
    text = text.strip()
    return f"{text[: max - 3].strip()}..." if len(text) > max else text


def format_preview(messages: typing.List[typing.Dict[str, typing.Any]]):
    """
    Used to format previews.

    Parameters
    ----------
    messages : List[Dict[str, Any]]
        A list of messages.

    Returns
    -------
    str
        A formatted string preview.
    """
    messages = messages[:3]
    out = ""
    for message in messages:
        if message.get("type") in {"note", "internal"}:
            continue
        author = message["author"]
        content = str(message["content"]).replace("\n", " ")
        name = author["name"] + "#" + str(author["discriminator"])
        prefix = "[M]" if author["mod"] else "[R]"
        out += truncate(f"`{prefix} {name}:` {content}", max=75) + "\n"

    return out or "No Messages"


def days(day: typing.Union[str, int]) -> str:
    """
    Humanize the number of days.

    Parameters
    ----------
    day: Union[int, str]
        The number of days passed.

    Returns
    -------
    str
        A formatted string of the number of days passed.
    """
    day = int(day)
    if day == 0:
        return "**today**"
    return f"{day} day ago" if day == 1 else f"{day} days ago"


def cleanup_code(content: str) -> str:
    """
    Automatically removes code blocks from the code.

    Parameters
    ----------
    content : str
        The content to be cleaned.

    Returns
    -------
    str
        The cleaned content.
    """
    # remove ```py\n```
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:-1])

    # remove `foo`
    return content.strip("` \n")


TOPIC_OTHER_RECIPIENTS_REGEX = re.compile(
    r"Other Recipients:\s*((?:\d{17,21},*)+)", flags=re.IGNORECASE
)
TOPIC_TITLE_REGEX = re.compile(r"\bTitle: (.*)\n(?:User ID: )\b", flags=re.IGNORECASE | re.DOTALL)
TOPIC_UID_REGEX = re.compile(r"\bUser ID:\s*(\d{17,21})\b", flags=re.IGNORECASE)


def match_title(text: str) -> str:
    """
    Matches a title in the format of "Title: XXXX"

    Parameters
    ----------
    text : str
        The text of the user ID.

    Returns
    -------
    Optional[str]
        The title if found.
    """
    match = TOPIC_TITLE_REGEX.search(text)
    if match is not None:
        return match.group(1)


def match_user_id(text: str) -> int:
    """
    Matches a user ID in the format of "User ID: 12345".

    Parameters
    ----------
    text : str
        The text of the user ID.

    Returns
    -------
    int
        The user ID if found. Otherwise, -1.
    """
    text = text.split("User ID ")[-1]
    if "," in text:
        text = text.split(",")[0]
    return int(text)


def match_other_recipients(text: str) -> typing.List[int]:
    """
    Matches a title in the format of "Other Recipients: XXXX,XXXX"

    Parameters
    ----------
    text : str
        The text of the user ID.

    Returns
    -------
    List[int]
        The list of other recipients IDs.
    """
    match = TOPIC_OTHER_RECIPIENTS_REGEX.search(text)
    if match is not None:
        return list(map(int, match.group(1).split(",")))
    return []


def create_not_found_embed(word, possibilities, name, n=2, cutoff=0.6) -> Embed:
    # Single reference of Color.red()
    embed = Embed(color=0xED4245, description=f"**{name.capitalize()} `{word}` cannot be found.**")
    if val := get_close_matches(word, possibilities, n=n, cutoff=cutoff):
        embed.description += "\nHowever, perhaps you meant...\n" + "\n".join(val)
    return embed


def parse_alias(alias, *, split=True):
    def encode_alias(m):
        return "\x1AU" + base64.b64encode(m.group(1).encode()).decode() + "\x1AU"

    def decode_alias(m):
        return base64.b64decode(m.group(1).encode()).decode()

    alias = re.sub(
        r"(?:(?<=^)(?:\s*(?<!\\)(?:\")\s*)|(?<=&&)(?:\s*(?<!\\)(?:\")\s*))(.+?)"
        r"(?:(?:\s*(?<!\\)(?:\")\s*)(?=&&)|(?:\s*(?<!\\)(?:\")\s*)(?=$))",
        encode_alias,
        alias,
    ).strip()

    aliases = []
    if not alias:
        return aliases

    if split:
        iterate = re.split(r"\s*&&\s*", alias)
    else:
        iterate = [alias]

    for a in iterate:
        a = re.sub("\x1AU(.+?)\x1AU", decode_alias, a)
        if a[0] == a[-1] == '"':
            a = a[1:-1]
        aliases.append(a)

    return aliases


def normalize_alias(alias, message=""):
    aliases = parse_alias(alias)
    contents = parse_alias(message, split=False)

    final_aliases = []
    for a, content in zip_longest(aliases, contents):
        if a is None:
            break

        if content:
            final_aliases.append(f"{a} {content}")
        else:
            final_aliases.append(a)

    return final_aliases


def format_description(i, names):
    return "\n".join(
        ": ".join((str(a + i * 15), b))
        for a, b in enumerate(takewhile(lambda x: x is not None, names), start=1)
    )


def trigger_typing(func):
    @functools.wraps(func)
    async def wrapper(self, ctx: CommandContext, *args, **kwargs):
        await ctx.client.trigger_typing(int(ctx.channel_id))
        return await func(self, ctx, *args, **kwargs)

    return wrapper


def escape_code_block(text):
    return re.sub(r"```", "`\u200b``", text)


def tryint(x):
    try:
        return int(x)
    except (ValueError, TypeError):
        return x


async def get_top_hoisted_role(guild: Guild, member: Member) -> Role:

    _roles = [await get(guild.roles, id=_) for _ in member.roles]
    roles: typing.List[Role] = sorted(_roles, key=lambda r: r.position, reverse=True)
    for role in roles:
        if role.hoist:
            return role


def get_joint_id(message: Message) -> typing.Optional[int]:
    """
    Get the joint ID from `discord.Embed().author.url`.
    Parameters
    -----------
    message : discord.Message
        The discord.Message object.
    Returns
    -------
    int
        The joint ID if found. Otherwise, None.
    """
    if message.embeds:
        with contextlib.suppress(ValueError):
            if url := getattr(message.embeds[0].author, "url", ""):
                return int(url.split("#")[-1])
    return None
