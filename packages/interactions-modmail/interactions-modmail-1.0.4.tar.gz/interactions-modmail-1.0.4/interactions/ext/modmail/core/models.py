import contextlib
import os
from enum import IntEnum
from string import Formatter

import _string

from interactions import Embed, InteractionException

try:
    from colorama import Fore, Style
except ImportError:
    Fore = Style = type("Dummy", (object,), {"__getattr__": lambda self, item: ""})()


if ".heroku" in os.environ.get("PYTHONHOME", ""):
    # heroku
    Fore = Style = type("Dummy", (object,), {"__getattr__": lambda self, item: ""})()


class PermissionLevel(IntEnum):
    OWNER = 5
    ADMINISTRATOR = 4
    ADMIN = 4
    MODERATOR = 3
    MOD = 3
    SUPPORTER = 2
    RESPONDER = 2
    REGULAR = 1
    INVALID = -1


class InvalidConfigError(InteractionException):
    def __init__(self, message, **kwargs):
        kwargs["message"] = message
        super().__init__(0, **kwargs)
        self.message = message

    @property
    def embed(self):
        return Embed(title="Error", description=self.message, color=0xED4245)


class _Default:
    pass


Default = _Default()


class SafeFormatter(Formatter):
    def get_field(self, field_name, args, kwargs):
        first, rest = _string.formatter_field_name_split(field_name)

        try:
            obj = self.get_value(first, args, kwargs)
        except (IndexError, KeyError):
            return "<Invalid>", first

        # loop through the rest of the field_name, doing
        #  getattr or getitem as needed
        # stops when reaches the depth of 2 or starts with _.
        with contextlib.suppress(IndexError, KeyError):
            for n, (is_attr, i) in enumerate(rest):
                if n >= 2:
                    break
                if is_attr:
                    if str(i).startswith("_"):
                        break
                    obj = getattr(obj, i)
                else:
                    obj = obj[i]
            else:
                return obj, first
        return "<Invalid>", first


class DMDisabled(IntEnum):
    NONE = 0
    NEW_THREADS = 1
    ALL_THREADS = 2


class HostingMethod(IntEnum):
    HEROKU = 0
    PM2 = 1
    SYSTEMD = 2
    SCREEN = 3
    DOCKER = 4
    OTHER = 5
