"""Miscellaneous utility functions"""

from __future__ import annotations

__all__ = (
    'MAX_NUMBER', 'format_bytes', 'format_timestamp', 'parse_bytes',
    'parse_duration', 'parse_extractor_arg', 'parse_ytdlp_dict',
    'parse_ytdlp_dicts', 'prompt_pass', 'split_seconds'
)

import getpass
import re
import warnings
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from typing import Any, Optional, TextIO

_BINARY_PREFIXES = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
"""List of binary (metric) prefixes

Used by `format_bytes()`
"""
_MAX_BINARY_PREFIX_INDEX = len(_BINARY_PREFIXES) - 1

_BINARY_REGEX = re.compile(
    fr'''
        \s*
        (?P<bytes>
            \d+(?:\.\d+)?
        )
        \s*
        (?P<prefix>
            # Match 0 or 1 characters from `_BINARY_PREFIXES`
            [{"".join(_BINARY_PREFIXES)}]?
        )
        i?B?
        \s*
    ''',
    flags=(re.IGNORECASE | re.VERBOSE)
)
"""Regex used by `parse_bytes()` to extract the size and unit from a
byte string"""

MAX_NUMBER = (2**53) - 1
"""Max number in JSON according to RFC 8259"""


def format_bytes(bytes_: float, max_precision: int = 2) -> str:
    """Return a human-readable representation of the given size in bytes

    max_precision: The result will be rounded to this many decimal
                   places
    """
    prefix_index = -1

    while bytes_ >= 1024 and prefix_index < _MAX_BINARY_PREFIX_INDEX:
        bytes_ /= 1024
        prefix_index += 1

    if prefix_index < 0:
        prefix = ''
    else:
        prefix = f'{_BINARY_PREFIXES[prefix_index]}i'

    rounded = round(bytes_, max_precision)
    return f'{rounded} {prefix}B'


def parse_bytes(byte_str: str) -> int:
    """Convert the given byte string to numeric bytes

    This is the inverse of `format_bytes()`
    """
    match = _BINARY_REGEX.fullmatch(byte_str)
    if not match:
        raise ValueError(f'Invalid byte string: {byte_str}')

    bytes_ = float(match.group('bytes'))
    prefix = match.group('prefix').upper()

    if prefix:
        for unit in _BINARY_PREFIXES:
            bytes_ *= 1024
            if unit == prefix:
                break

    return round(bytes_)


def split_seconds(seconds: float) -> tuple[int, int, int]:
    """Split the given seconds into a 3-length tuple containing the
    total hours, minutes, and seconds (h, min, s)

    The seconds in the result are rounded to the nearest int

    Example:
      4000 -> (1, 6, 40)
    """
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return int(hours), int(minutes), round(seconds)


def format_timestamp(timestamp: str) -> str:
    """Format the given ISO timestamp into a user-readable str

    `locale.setlocale()` should be called first so that it uses the
    user's locale-specific format
    """
    datetime_ = datetime.fromisoformat(timestamp).astimezone()
    # %c = Locale's appropriate date and time representation.
    return datetime_.strftime('%c')


def prompt_pass(
    prompt: str = 'Password: ', stream: Optional[TextIO] = None
) -> str:
    """Prompt the user for a password, and return the input

    Ignores `GetPassWarning`, which is raised by `getpass()` when it
    falls back to reading from stdin.
    Note that a single warning line is still printed.

    Raises `EOFError` if it's unable to read anything
    """
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=getpass.GetPassWarning)
        password = getpass.getpass(prompt, stream)
    return password


def parse_ytdlp_dict(
    arg: str, *, allowed_keys: str = r'[\w-]+',
    delimiter: str = ':', default_key: Optional[str] = None,
    process: Optional[Callable[[str], Any]] = None, multiple_keys: bool = True
) -> dict[str, Any]:
    """Convert a yt-dlp style `KEY:VALUE` argument to a dict

    Based on the yt-dlp source:
        https://github.com/yt-dlp/yt-dlp/blob/c588b602d34f005dc018ae004281226741414192/yt_dlp/options.py#L152-L174

    arg: `KEY:VALUE` str that will be converted to a dict
    allowed_keys: Regex used to match keys. Case-insensitive
    delimiter: Character used to separate the key and value
    default_key: If the regex doesn't match, the entire string will be
        used as the value, and this will be used as the key. If `None`,
        ValueError will be raised.
    process: Values will be converted using this function if not `None`.
        Otherwise, the string value will be used as-is
    multiple_keys: Whether or not to allow specifying multiple keys with
        the same value, eg, `KEY1,KEY2:VALUE`

    All keys are converted to lowercase
    """
    return_dict: dict[str, Any] = {}

    if multiple_keys:
        allowed_keys = f'({allowed_keys})(,({allowed_keys}))*'

    match = re.fullmatch(
        f'(?P<keys>{allowed_keys}){delimiter}(?P<value>.*)', arg, re.IGNORECASE
    )
    if match:
        keys_group = match.group('keys').lower()
        keys: Iterable[str] = (key.strip() for key in keys_group.split(','))
        value = match.group('value')
    elif default_key is not None:
        keys = (default_key,)
        value = arg
    else:
        raise ValueError(f'Invalid arg: {arg}')

    if process is not None:
        value = process(value)

    for key in keys:
        return_dict[key] = value
    return return_dict


def parse_ytdlp_dicts(
    args: Iterable[str], *, allowed_keys: str = r'[\w-]+',
    delimiter: str = ':', default_key: Optional[str] = None,
    process: Optional[Callable[[str], Any]] = None, multiple_keys: bool = True
) -> dict[str, Any]:
    """Wrapper for `parse_ytdlp_dict()` that parses a list of args

    The resulting dicts are merged together

    All kwargs are the same as `parse_ytdlp_dict()`
    """
    return_dict: dict[str, Any] = {}

    for arg in args:
        arg_dict = parse_ytdlp_dict(
            arg, allowed_keys=allowed_keys, delimiter=delimiter,
            default_key=default_key, process=process,
            multiple_keys=multiple_keys
        )
        return_dict.update(arg_dict)

    return return_dict


def parse_extractor_arg(args: str) -> dict[str, tuple[str, ...]]:
    """Split the extractor_args args into a dict

    This is used as the `process` kwarg to `parse_ytdlp_dict()` for the
    --extractor-args yt-dlp argument.

    Example input:
        'player_client=android_agegate,web;include_live_dash'

    Example output:
        {
          'player_client': ('android_agegate', 'web'),
          'include_live_dash': ('',)
        }

    See https://github.com/yt-dlp/yt-dlp#extractor-arguments for info
    about the format.

    Based on the yt-dlp source:
        https://github.com/yt-dlp/yt-dlp/blob/c588b602d34f005dc018ae004281226741414192/yt_dlp/options.py#L1521-L1532
    """
    return_dict: dict[str, tuple[str, ...]] = {}

    for arg in args.split(';'):
        split_arg = arg.split('=', maxsplit=1)
        key = split_arg[0].strip().lower().replace('-', '_')

        if len(split_arg) == 1:
            # Set the values to a single empty str if the arg is just a
            # key
            return_dict[key] = ('',)
        else:
            values = split_arg[1].split(',')
            return_dict[key] = tuple(value.strip() for value in values)

    return return_dict


_DURATION_REGEXES = (
    # Match a duration roughly in the form 'DD:HH:MM:SS.SS'
    re.compile(
        r'''
            (?:
                (?:
                    (?:
                        (?P<days>[0-9]+):
                    )?
                    (?P<hours>[0-9]+):
                )?
                (?P<mins>[0-9]+):
            )?
            (?P<secs>[0-9]+)
            (?P<ms>\.[0-9]+)?
            Z?
        ''',
        flags=re.VERBOSE
    ),

    # Match an ISO-8601 duration such as 'P3Y6M4DT12H30M5S'.
    # Not fully compliant with the ISO spec.
    # The years, months, and weeks are ignored for some reason.
    re.compile(
        r'''
            (?:
                P?
                (?:
                    [0-9]+\s*y(?:ears?)?\s*
                )?
                (?:
                    [0-9]+\s*m(?:onths?)?\s*
                )?
                (?:
                    [0-9]+\s*w(?:eeks?)?\s*
                )?
                (?:
                    (?P<days>[0-9]+)\s*d(?:ays?)?\s*
                )?
                T
            )?
            (?:
                (?P<hours>[0-9]+)\s*h(?:ours?)?\s*
            )?
            (?:
                (?P<mins>[0-9]+)\s*m(?:in(?:ute)?s?)?\s*
            )?
            (?:
                (?P<secs>[0-9]+)(?P<ms>\.[0-9]+)?\s*s(?:ec(?:ond)?s?)?\s*
            )?
            Z?
        ''',
        flags=(re.VERBOSE | re.IGNORECASE)
    ),

    # Match a duration roughly in the form 'HH.HH hours' or 'MM.MM min'
    re.compile(
        r'''
            (?:
                (?P<hours>[0-9.]+)\s*(?:hours?)
                |
                (?P<mins>[0-9.]+)\s*(?:mins?\.?|minutes?)
            )
            \s*
            Z?
        ''',
        flags=(re.VERBOSE | re.IGNORECASE)
    )
)
"""List of regexes that will be used by `parse_duration()` to convert
strings

The first matching regex will be used.

The regexes should return at least one of the groups in
`_DURATION_UNITS`. If a group isn't matched, its value is assumed to be
zero.
"""


_DURATION_UNITS = (
    ('days', 86400), ('hours', 3600), ('mins', 60), ('secs', 1), ('ms', 1)
)
"""List of match-groups returned by the regexes in `_DURATION_REGEXES`
with their corresponding value in seconds"""


def parse_duration(value: str) -> float:
    """Convert a string duration to the corresponding value in seconds

    Raises `ValueError` if the string isn't a valid duration.

    Regexes are based on the yt-dlp source:
        https://github.com/yt-dlp/yt-dlp/blob/d0d012d4e79cd1420e96ce5c3d509771110d3ea1/yt_dlp/utils.py#L3965-L4020
    """
    value = value.strip()

    # Use the first regex in `_DURATION_REGEXES` that matches the value
    for regex in _DURATION_REGEXES:
        match = regex.fullmatch(value)
        if match:
            groups = match.groupdict()
            break
    else:
        raise ValueError(f'Invalid duration: {value}')

    duration = 0.0
    for unit, factor in _DURATION_UNITS:
        group_value = groups.get(unit, 0)
        if group_value:
            duration += (float(group_value) * factor)

    return duration
