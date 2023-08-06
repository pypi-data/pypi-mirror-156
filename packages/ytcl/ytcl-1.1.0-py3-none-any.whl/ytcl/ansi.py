"""ANSI escape code utilities

Reference: https://en.wikipedia.org/wiki/ANSI_escape_code#Description

In order to maintain compatibility with Windows, only escape codes that
are supported by Colorama are used.
See https://github.com/tartley/colorama#recognised-ansi-sequences
"""

from __future__ import annotations

__all__ = (
    'CSI', 'Brightness', 'EraseMode', 'FGColor', 'erase_in_line',
    'format_fg_color', 'format_brightness', 'reset_color', 'reset_line',
    'set_fg_color', 'set_brightness'
)

import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Optional

CSI = '\033['
"""ANSI control sequence indicator"""


class _EscapeEnum(enum.IntEnum):
    """Subclass of `IntEnum` that's safe to use with functions within
    this module"""
    def __str__(self) -> str:
        """Return the value when converted to a string

        This allows the enum to work as an escape code when printed.
        """
        return str(self.value)


class FGColor(_EscapeEnum):
    """Enum of foreground colors that can be set using `set_fg_color()`"""
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    RESET = 39


class Brightness(_EscapeEnum):
    """Enum of brightness levels"""
    BOLD = 1
    NORMAL = 22


class EraseMode(_EscapeEnum):
    """Enum that represents the mode used by `erase_in_line()`"""
    END = 0
    BEGINNING = 1
    ENTIRE = 2


def set_fg_color(color: int, brightness: Optional[int] = None) -> str:
    """Set the foreground color, and optionally the brightness

    If `brightness` isn't given, the brightness won't be changed.

    See the `FGColor` and `Brightness` enums for possible color values.
    """
    if brightness is not None:
        return f'{CSI}{brightness};{color}m'
    else:
        return f'{CSI}{color}m'


def set_brightness(brightness: int) -> str:
    """Set the brightness

    See the `Brightness` enum for possible brightness values.
    """
    return f'{CSI}{brightness}m'


def reset_color() -> str:
    """Reset all color attributes

    Resets the foreground color, background color, and brightness.
    """
    return f'{CSI}0m'


def format_fg_color(
    msg: Any, color: int, brightness: int = Brightness.NORMAL
) -> str:
    """Format `msg` with the given foreground-color and brightness

    The color is reset after the message.

    Equivalent to
    `set_fg_color(color, brightness) + msg + reset_color()`.
    """
    return f'{set_fg_color(color, brightness)}{msg}{reset_color()}'


def format_brightness(
    msg: Any, brightness: int = Brightness.BOLD
) -> str:
    """Format `msg` with the given brightness

    The color is reset after the message.

    Equivalent to
    `set_brightness(brightness) + msg + reset_color()`.
    """
    return f'{set_brightness(brightness)}{msg}{reset_color()}'


def erase_in_line(mode: int = EraseMode.ENTIRE) -> str:
    """Erase part of the current line

    EraseMode.END: Clear from cursor to the end of the line.
    EraseMode.BEGINNING: Clear from cursor to the beginning of the line.
    EraseMode.ENTIRE: Clear the entire line.
    """
    return f'{CSI}{mode}K'


def reset_line() -> str:
    r"""Erase the current line and set the cursor to the beginning of it

    Equivalent to `\r + erase_in_line()`.
    """
    return f'\r{erase_in_line()}'
