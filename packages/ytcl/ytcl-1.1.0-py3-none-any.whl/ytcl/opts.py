"""Convert argparse args to ytdl_opts and custom_opts"""

from __future__ import annotations

__all__ = (
    'create_ytdl_opts', 'create_custom_opts', 'CustomOpt',
    'CustomOptHandlerArgs', 'YTDLOpt', 'YTDLOptHandlerArgs',
    'PostProcessorOpt', 'CUSTOM_OPTS', 'YTDL_OPTS', 'POSTPROCESSOR_OPTS',
    'OMIT_OPT'
)

import logging
import os
import re
import shlex
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .error import (
    CustomOptNotWhitelistedError, InvalidArgError, YTDLOptNotWhitelistedError
)
from .util import (
    MAX_NUMBER, parse_bytes, parse_duration, parse_extractor_arg,
    parse_ytdlp_dicts, prompt_pass
)

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Iterable, Sequence
    from typing import Any, Optional, Union
    import argparse

    from .config import YTDLConfig

OMIT_OPT = object()
"""If this is returned by `YTDLOpt.handler()` or `CustomOpt.handler()`,
the option won't be added to ytdl_opts/custom_opts"""


def create_ytdl_opts(
    args: argparse.Namespace, config: YTDLConfig
) -> Optional[dict[str, Any]]:
    """Create the ytdl_opts dict based on the given argparse namespace
    and YTDLConfig

    The argparse parser should be generated using `args.get_parser()`.

    The argparse namespace may be modified in order to add additional
    ytdl_opts that are implied by other ytdl_opts.

    Returns `None` if there are no ytdl_opts.
    """
    ytdl_opts = {}
    postprocessors = []

    # Parse postprocessor args
    #
    # This must be run before parsing YTDL_OPTS so that the
    # postprocessor args can modify the argparse namespace
    for pp_opt in POSTPROCESSOR_OPTS:
        postprocessor = pp_opt.get_postprocessor(args, config)
        if postprocessor:
            postprocessors.append(postprocessor)

    # Parse all other args
    for ytdl_opt in YTDL_OPTS:
        pair = ytdl_opt.get_pair(args, config)
        if pair:
            ytdl_opts[pair[0]] = pair[1]

    # Add the postprocessors to ytdl_opts only if it isn't empty
    if postprocessors:
        if not config.is_ytdl_whitelisted('postprocessors'):
            raise YTDLOptNotWhitelistedError('postprocessors')
        ytdl_opts['postprocessors'] = tuple(postprocessors)

    if ytdl_opts:
        return ytdl_opts
    else:
        return None


def create_custom_opts(
    args: argparse.Namespace, config: YTDLConfig
) -> Optional[dict[str, Any]]:
    """Create the custom_opts dict based on the given argparse namespace
    and YTDLConfig

    The argparse parser should be generated using `args.get_parser()`.

    Returns `None` if there are no custom_opts.
    """
    custom_opts: dict[str, Any] = {}

    for custom_opt in CUSTOM_OPTS:
        pair = custom_opt.get_pair(args, config)
        if pair:
            custom_opts[pair[0]] = pair[1]

    if custom_opts:
        return custom_opts
    else:
        return None


@dataclass(frozen=True)
class CustomOptHandlerArgs:
    """Dataclass used as the argument to `CustomOpt.handler()`"""

    namespace: argparse.Namespace
    """The argparse namespace

    This can be used to get the value of args.

    You can also use it to modify args, but keep in mind, that the
    modified value will only be used if the arg that you modified is
    parsed *after* the current arg.

    Options are parsed in the following order:
        CUSTOM_OPTS -> POSTPROCESSOR_OPTS -> YTDL_OPTS
    """
    config: YTDLConfig
    """Config of the ytdl-server

    You can use this to check default ytdl_opts, check the whitelist,
    etc.
    """


@dataclass(frozen=True)
class YTDLOptHandlerArgs(CustomOptHandlerArgs):
    """Dataclass used as the argument to `YTDLOpt.handler()` and
    `PostProcessorOpt.handler()`"""

    arg: str
    """Name of the argparse argument"""
    value: Any
    """The value of the argument, taken from the namespace"""


@dataclass(frozen=True)
class YTDLOpt:
    """Dataclass used to convert argparse args to a single ytdl_opt"""

    ytdl_opt: str
    """Name of the key that will be added to ytdl_opts"""
    # Ignore type warning about `None` not being compatible. The value
    # is converted to a str in `__post_init__()`
    arg: str = None  # type: ignore[assignment]
    """Name of the arg within the argparse namespace

    Defaults to the same value as `ytdl_opt`
    """
    handler: Optional[Callable[[YTDLOptHandlerArgs], Any]] = None
    """Function that will be used to check the argparse arg and/or
    convert it to the proper value that will be added to ytdl_opts

    If not given, the argparse arg will be added to ytdl_opts as-is

    The function should return the converted value, which will be added
    to the ytdl_opts dict.

    If the function returns `OMIT_OPT`, the ytdl_opt won't be added to
    ytdl_opts.

    If the function raises `InvalidArgError`, the exception will be
    caught and passed to the user.
    """

    def __post_init__(self) -> None:
        if self.arg is None:
            object.__setattr__(self, 'arg', self.ytdl_opt)

    def get_pair(
        self, args: argparse.Namespace, config: YTDLConfig
    ) -> Optional[tuple[str, Any]]:
        """Get the value of the ytdl_opt from the given namespace.

        Returns a tuple-pair containing the key and the value. This can
        be added to ytdl_opts.

        Returns `None` if the arg doesn't exist in the namespace, or if
        the handler decides that the option should be skipped.

        Raises YTDLOptNotWhitelistedError if the ytdl_opt isn't
        whitelisted.
        """
        if self.arg not in args:
            return None

        if not config.is_ytdl_whitelisted(self.ytdl_opt):
            raise YTDLOptNotWhitelistedError(self.ytdl_opt)

        value = getattr(args, self.arg)
        if self.handler is not None:
            handler_args = YTDLOptHandlerArgs(
                namespace=args, config=config, arg=self.arg, value=value
            )
            value = self.handler(handler_args)

            if value is OMIT_OPT:
                return None

        return self.ytdl_opt, value


@dataclass(frozen=True)
class PostProcessorOpt:
    """Dataclass used to create ytdl postprocessors from argparse args"""

    arg: str
    """Name of the arg within the argparse namespace

    `handler` will only be called if this arg exists
    """
    handler: Callable[[YTDLOptHandlerArgs], Optional[dict[str, Any]]]
    """Function that will be used to generate the postprocessor dict

    The function should return a postprocessor dict, which will be
    appended to the 'postprocessors' list in `ytdl_opts`.
    It can also return `None`, in which case nothing will be added.

    If the function raises `InvalidArgError`, the exception will be
    caught and passed to the user.
    """

    def get_postprocessor(
        self, args: argparse.Namespace, config: YTDLConfig
    ) -> Optional[dict[str, Any]]:
        """Generate the postprocessor dict based on the given namespace

        This dict should be appended to the 'postprocessors' list in
        ytdl_opts

        Returns `None` if the arg doesn't exist in the namespace.
        """
        if self.arg not in args:
            return None

        value = getattr(args, self.arg)
        handler_args = YTDLOptHandlerArgs(
            namespace=args, config=config, arg=self.arg, value=value
        )

        # mypy incorrectly infers the type of callable objects when
        # using a frozen dataclass:
        # https://github.com/python/mypy/issues/7404
        postprocessor: dict[str, Any] = self.handler(  # type: ignore
            handler_args
        )
        return postprocessor


@dataclass(frozen=True)
class CustomOpt:
    """Dataclass used to convert argparse args to a custom_opt"""

    custom_opt: str
    """Name of the key that will be added to custom_opts"""
    args: tuple[str, ...]
    """Name of the args within the argparse namespace

    `handler()` will be called if *any* of the args exist
    """
    handler: Optional[Callable[[CustomOptHandlerArgs], Any]] = None
    """Function that will be used to check the argparse args and convert
    them to the value that will be added to custom_opts

    If not given, the value of the *first* arg that exists will be used.

    The function should return the converted value, which will be added
    to the custom_opts dict.

    If the function returns `OMIT_OPT`, the custom_opt won't be added to
    custom_opts.

    If the function raises `InvalidArgError`, the exception will be
    caught and passed to the user.
    """

    def get_pair(
        self, args: argparse.Namespace, config: YTDLConfig
    ) -> Optional[tuple[str, Any]]:
        """Get the value of the custom_opt from the given namespace.

        Returns a tuple-pair containing the key and the value. This can
        be added to custom_opts.

        Returns `None` if the arg doesn't exist in the namespace, or if
        the handler decides that the option should be skipped.

        Raises CustomOptNotWhitelistedError if the custom_opt isn't
        whitelisted.
        """
        for arg in self.args:
            if arg in args:
                first_arg = arg
                break
        else:
            return None

        if not config.is_custom_whitelisted(self.custom_opt):
            raise CustomOptNotWhitelistedError(self.custom_opt)

        if self.handler is None:
            # Return the value of the first arg that exists
            value = getattr(args, first_arg)
        else:
            # Use `handler()` to get the value
            handler_args = CustomOptHandlerArgs(
                namespace=args, config=config
            )
            value = self.handler(handler_args)

            if value is OMIT_OPT:
                return None

        return self.custom_opt, value


def _custom_extractaudio(
    args: CustomOptHandlerArgs
) -> Optional[dict[str, Any]]:
    """Generate the 'extractaudio' custom_opt"""
    # Disable the custom_opt if --no-extract-audio is given
    extractaudio: bool = args.namespace.extract_audio
    if not extractaudio:
        return None

    # Verify that the output template contains a file extension.
    #
    # This just verifies that it contains a non-leading period, which
    # isn't a very accurate way of doing it, but it's the way that
    # youtube-dl checks it
    outtmpl: Optional[str] = args.config.ytdl_opt_from_args(
        args.namespace, 'outtmpl', 'output', None
    )
    if outtmpl is not None:
        ext = os.path.splitext(outtmpl)[1]
        if not ext:
            raise InvalidArgError(
                'extract_audio',
                'Cannot download a video and extract audio into the same '
                f'file. Use "{outtmpl}.%(ext)s" instead of "{outtmpl}" as the '
                'output template'
            )

    return {
        'audioformat': args.namespace.audio_format,
        'audioquality': args.namespace.audio_quality,
        'nopostoverwrites': args.namespace.no_post_overwrites
    }


def _custom_remuxvideo(args: CustomOptHandlerArgs) -> Optional[str]:
    """Generate the 'remuxvideo' custom_opt

    Spaces are removed from the value in order to match the behavior of
    yt-dlp.
    """
    # Disable the custom_opt if --no-remux-video is given
    remuxvideo: Optional[str] = args.namespace.remux_video
    if remuxvideo is None:
        return None

    remuxvideo = remuxvideo.replace(' ', '')
    recodevideo: Optional[str] = args.config.custom_opt_from_args(
        args.namespace, 'recodevideo', 'recode_video', None
    )
    if recodevideo is not None:
        logging.warning(
            '--remux-video is ignored because it conflicts with --recode-video'
        )
        return None

    return remuxvideo


def _custom_recodevideo(args: CustomOptHandlerArgs) -> Optional[str]:
    """Generate the 'recodevideo' custom_opt

    Spaces are removed from the value in order to match the behavior of
    yt-dlp. This technically breaks backwards-compatibility with
    youtube-dl, but there's no valid reason for it to contain whitespace
    in the first place.
    """
    # Disable the custom_opt if --no-recode-video is given
    recodevideo: Optional[str] = args.namespace.recode_video
    if recodevideo is None:
        return None

    recodevideo = recodevideo.replace(' ', '')
    return recodevideo


def _custom_split_chapters(
    args: CustomOptHandlerArgs
) -> Optional[dict[str, Any]]:
    """Generate the 'split_chapters' custom_opt"""
    # Disable the custom_opt if --no-split-chapters is given
    split_chapters: bool = args.namespace.split_chapters
    if not split_chapters:
        return None

    force_keyframes: bool = args.namespace.force_keyframes_at_cuts
    return {
        'force_keyframes': force_keyframes
    }


def _custom_sponsorblock(
    args: CustomOptHandlerArgs
) -> Optional[dict[str, Any]]:
    """Generate the 'sponsorblock' custom_opt"""
    # Disable the custom_opt if --no-sponsorblock is given
    no_sponsorblock: bool = getattr(args.namespace, 'no_sponsorblock', False)
    if no_sponsorblock:
        return None

    mark: Optional[tuple[str, ...]] = getattr(
        args.namespace, 'sponsorblock_mark', None
    )
    remove: Optional[tuple[str, ...]] = getattr(
        args.namespace, 'sponsorblock_remove', None
    )
    template: Optional[str] = getattr(
        args.namespace, 'sponsorblock_chapter_title', None
    )
    api: Optional[str] = getattr(args.namespace, 'sponsorblock_api', None)
    force_keyframes: bool = args.namespace.force_keyframes_at_cuts

    sponsorblock: dict[str, Any] = {
        'force_keyframes': force_keyframes
    }

    if mark:
        sponsorblock['mark'] = tuple(s.lower() for s in mark)
    if remove:
        sponsorblock['remove'] = tuple(s.lower() for s in remove)
    if template is not None:
        sponsorblock['template'] = template
    if api is not None:
        sponsorblock['api'] = api

    return sponsorblock


def _parse_interpreters(
    parse_metadata: Iterable[str]
) -> Generator[dict[str, str], None, None]:
    r"""Split the parse_metadata arguments into the format accepted by
    the custom_opt

    Each item is split into two values at the first colon (':').
    A literal colon can be escaped with a backslash, eg r'\:'.

    Example input:
        ['FROM:TO', r'ESC\:APE:TO', ':ONLY_TO']

    Example output:
        (
            {'from': 'FROM',    'to': 'TO'  },
            {'from': 'ESC:APE', 'to': 'TO' },
            {'from': '',        'to': 'ONLY_TO'}
        )

    Based on the yt-dlp source:
        https://github.com/yt-dlp/yt-dlp/blob/013b50b7949563e445936302d6e486bab7100018/yt_dlp/postprocessor/metadataparser.py#L100-L108
    """
    for interpreter in parse_metadata:
        match = re.fullmatch(r'(?P<from>.*?)(?<!\\):(?P<to>.+)', interpreter)
        if not match:
            raise InvalidArgError(
                'parse_metadata', f'invalid interpreter: {interpreter}'
            )

        yield {
            # Unescape the colons within the 'from' group
            'from': match.group('from').replace(r'\:', ':'),
            'to': match.group('to')
        }


def _custom_parse_metadata(
    args: CustomOptHandlerArgs
) -> Optional[tuple[dict[str, str], ...]]:
    """Generate the 'parse_metadata' custom_opt"""
    parse_metadata: Optional[list[str]] = args.namespace.parse_metadata
    # Disable the custom_opt if --no-parse-metadata is given
    if parse_metadata is None:
        return None

    interpreters = _parse_interpreters(parse_metadata)
    return tuple(interpreters)


def _parse_replacers(
    replace_in_metadata: Iterable[Sequence[str]]
) -> Generator[dict[str, Union[str, tuple[str, ...]]], None, None]:
    """Split the replace_in_metadata arguments into the format accepted
    by the custom_opt

    Example input:
        [
            ['FIELD1,FIELD2', 'REGEX1', 'REPLACE1'],
            ['FIELD3', 'REGEX2', 'REPLACE2']
        ]

    Example output:
        (
            {
                'fields': ('FIELD1', 'FIELD2'),
                'regex': 'REGEX1',
                'replace': 'REPLACE1'
            },
            {
                'fields': ('FIELD3',),
                'regex': 'REGEX2',
                'replace': 'REPLACE2'
            }
        )
    """
    for replacer in replace_in_metadata:
        yield {
            'fields': tuple(replacer[0].split(',')),
            'regex': replacer[1],
            'replace': replacer[2]
        }


def _custom_replace_in_metadata(
    args: CustomOptHandlerArgs
) -> Optional[tuple[dict[str, Union[str, tuple[str, ...]]], ...]]:
    """Generate the 'replace_in_metadata' custom_opt"""
    # Disable the custom_opt if --no-replace-in-metadata is given
    replace_in_metadata: Optional[list[list[str]]] = (
        args.namespace.replace_in_metadata
    )
    if replace_in_metadata is None:
        return None

    replacers = _parse_replacers(replace_in_metadata)
    return tuple(replacers)


def _parse_range(value: str) -> tuple[float, float]:
    """Parse a range used by the remove_chapters custom_opt

    Raises `ValueError` if the range is invalid.
    """
    # Remove leading '*'
    value = value[1:]
    start, end = value.split('-', maxsplit=1)

    start_duration = min(parse_duration(start), MAX_NUMBER)
    end_duration = min(parse_duration(end), MAX_NUMBER)

    if end_duration <= start_duration:
        raise InvalidArgError(
            'remove_chapters',
            'start duration must be less than the end duration: '
            f'*{value} ({start_duration}-{end_duration})'
        )

    return start_duration, end_duration


def _custom_remove_chapters(
    args: CustomOptHandlerArgs
) -> Optional[dict[str, Any]]:
    """Generate the 'remove_chapters' custom_opt"""
    # Disable the custom_opt if --no-remove-chapters is given
    remove_chapters: Optional[list[str]] = args.namespace.remove_chapters
    if remove_chapters is None:
        return None

    force_keyframes: bool = args.namespace.force_keyframes_at_cuts

    patterns: list[str] = []
    ranges: list[tuple[float, float]] = []

    for arg in remove_chapters:
        if arg.startswith('*'):
            # arg is a range
            try:
                range_ = _parse_range(arg)
            except ValueError as e:
                raise InvalidArgError(
                    'remove_chapters', f'invalid range: {arg}'
                ) from e

            ranges.append(range_)
        else:
            # arg is a pattern
            patterns.append(arg)

    return_dict: dict[str, Any] = {
        'force_keyframes': force_keyframes
    }
    if patterns:
        return_dict['patterns'] = patterns
    if ranges:
        return_dict['ranges'] = ranges

    return return_dict


def _check_playlistend(args: YTDLOptHandlerArgs) -> int:
    """Assert that playlistend >= playliststart"""
    playlist_end: int = args.value

    # A value of `-1` is equivalent to `None`, so we skip the check
    if playlist_end == -1:
        return playlist_end

    if 'playlist_start' in args.namespace:
        playlist_start: int = args.namespace.playlist_start
        if playlist_end < playlist_start:
            raise InvalidArgError(
                args.arg,
                'playlist_end must be greater-than-or-equal-to '
                f'playlist_start: {playlist_start} - {playlist_end}'
            )

    return playlist_end


def _size_from_str(args: YTDLOptHandlerArgs) -> int:
    """Convert the given size str (eg, '12 GB') to its size in bytes"""
    byte_str: str = args.value

    try:
        bytes_ = parse_bytes(byte_str)
    except ValueError as e:
        raise InvalidArgError(args.arg, f'invalid size: {byte_str}') from e

    return bytes_


def _parse_retries(args: YTDLOptHandlerArgs) -> int:
    """Convert the 'retries' arg to an int

    'inf' and 'infinite' are converted to the largest int allowed

    Also asserts that the value is >= 0
    """
    retries: str = args.value

    if retries in {'inf', 'infinite'}:
        return MAX_NUMBER

    try:
        retries_int = int(retries)
    except ValueError as e:
        raise InvalidArgError(args.arg, f'invalid number: {retries}') from e

    if retries_int < 0:
        raise InvalidArgError(args.arg, f'must be positive: {retries}')

    return min(retries_int, MAX_NUMBER)


def _shell_split(args: YTDLOptHandlerArgs) -> tuple[str, ...]:
    """Split the given arg using shell-like syntax"""
    cmd: str = args.value

    try:
        split = shlex.split(cmd)
    except ValueError as e:
        raise InvalidArgError(args.arg, f'{e}: {cmd!r}') from e

    return tuple(split)


def _negate_bool(args: YTDLOptHandlerArgs) -> bool:
    """Negate the given bool"""
    return not args.value


def _check_max_sleep_interval(args: YTDLOptHandlerArgs) -> int:
    """Assert that max_sleep_interval >= sleep_interval"""
    if 'sleep_interval' not in args.namespace:
        raise InvalidArgError(
            args.arg, 'missing argument: --min-sleep-interval'
        )

    min_sleep_interval: int = args.namespace.sleep_interval
    max_sleep_interval: int = args.value

    if max_sleep_interval < min_sleep_interval:
        raise InvalidArgError(
            args.arg,
            'max_sleep_interval must be greater-than-or-equal-to '
            'min_sleep_interval: '
            f'{min_sleep_interval} - {max_sleep_interval}'
        )

    return max_sleep_interval


def _set_writesubtitles(args: YTDLOptHandlerArgs) -> bool:
    """Ensure that either 'writesubtitles' or 'writeautomaticsub' is
    `True` when 'allsubtitles' is `True`

    'allsubtitles' has no effect if this isn't the case
    """
    allsubtitles: bool = args.value

    if allsubtitles:
        writeautomaticsub: bool = args.config.ytdl_opt_from_args(
            args.namespace, 'writeautomaticsub', 'write_auto_sub', False
        )
        if not writeautomaticsub:
            logging.debug(
                'Implicitly setting write_sub to True so that allsubtitles '
                'will work'
            )
            args.namespace.write_sub = True

    return allsubtitles


def _check_username(args: YTDLOptHandlerArgs) -> str:
    """Assert that --username isn't used with --netrc, and prompt for
    the password if it wasn't supplied"""
    usenetrc: bool = args.config.ytdl_opt_from_args(
        args.namespace, 'usenetrc', 'netrc', False
    )
    if usenetrc:
        raise InvalidArgError(
            args.arg, '--netrc cannot be used with --username'
        )

    username: str = args.value
    # Don't check the default opts because it doesn't make sense to use
    # a different username without changing the password
    password: Optional[str] = getattr(args.namespace, 'password', None)

    if password is None:
        logging.info('Username: %s', username)

        try:
            args.namespace.password = prompt_pass('Enter account password: ')
        except EOFError as e:
            raise InvalidArgError(
                'password', f'unable to prompt for the password: {e!r}'
            ) from e

    return username


def _check_password(args: YTDLOptHandlerArgs) -> str:
    """Assert that --password isn't used with --netrc, and that it isn't
    given without --username"""
    usenetrc: bool = args.config.ytdl_opt_from_args(
        args.namespace, 'usenetrc', 'netrc', False
    )
    if usenetrc:
        raise InvalidArgError(
            args.arg, '--netrc cannot be used with --password'
        )

    username: Optional[str] = args.config.ytdl_opt_from_args(
        args.namespace, 'username', default=None
    )
    if username is None:
        raise InvalidArgError(args.arg, 'missing argument: --username')

    password: str = args.value
    return password


def _check_ap_username(args: YTDLOptHandlerArgs) -> str:
    """Prompt for the AP password if it wasn't supplied"""
    ap_username: str = args.value
    # Don't check the default opts because it doesn't make sense to use
    # a different username without changing the password
    ap_password: Optional[str] = getattr(args.namespace, 'ap_password', None)

    if ap_password is None:
        logging.info('AP Username: %s', ap_username)

        try:
            args.namespace.ap_password = prompt_pass(
                'Enter TV provider account password: '
            )
        except EOFError as e:
            raise InvalidArgError(
                'ap_password', f'unable to prompt for the AP password: {e!r}'
            ) from e

    return ap_username


def _check_ap_password(args: YTDLOptHandlerArgs) -> str:
    """Assert that --ap-password isn't given without --ap-username"""
    ap_username: Optional[str] = args.config.ytdl_opt_from_args(
        args.namespace, 'ap_username', default=None
    )
    if ap_username is None:
        raise InvalidArgError(
            args.arg, 'missing argument: --ap-username'
        )

    ap_password: str = args.value
    return ap_password


def _parse_downloader(args: YTDLOptHandlerArgs) -> Union[dict[str, str], str]:
    """Convert --external-downloader to a yt-dlp dict

    If no keys are matched, the value is returned by itself in order to
    remain backwards-compatible with youtube-dl
    """
    downloaders: list[str] = args.value
    downloader_dict = parse_ytdlp_dicts(
        downloaders, default_key='default', process=str.strip
    )

    if len(downloader_dict) == 1 and 'default' in downloader_dict:
        # Return the value as-is if no keys were matched
        return downloaders[-1]
    else:
        return downloader_dict


def _parse_downloader_args(
    args: YTDLOptHandlerArgs
) -> Union[dict[str, tuple[str, ...]], tuple[str, ...]]:
    """Convert --external-downloader-args to a yt-dlp dict

    If no keys are matched, the value is returned by itself in order to
    remain backwards-compatible with youtube-dl
    """
    downloader_args: list[str] = args.value
    try:
        downloader_args_dict = parse_ytdlp_dicts(
            downloader_args, default_key='default', process=shlex.split
        )
    except ValueError as e:
        raise InvalidArgError(args.arg, f'{e}: {downloader_args}') from e

    if len(downloader_args_dict) == 1 and 'default' in downloader_args_dict:
        # Return the default value if no keys were matched
        return tuple(downloader_args_dict['default'])
    else:
        return {
            key: tuple(value) for key, value in downloader_args_dict.items()
        }


def _parse_ppa(
    args: YTDLOptHandlerArgs
) -> Union[dict[str, tuple[str, ...]], tuple[str, ...]]:
    """Convert --postprocessor-args to a yt-dlp dict

    If no keys are matched, the value is returned by itself in order to
    remain backwards-compatible with youtube-dl
    """
    pp_args: list[str] = args.value
    try:
        pp_args_dict = parse_ytdlp_dicts(
            pp_args, allowed_keys=r'\w+(?:\+\w+)?', default_key='default',
            process=shlex.split, multiple_keys=False
        )
    except ValueError as e:
        raise InvalidArgError(args.arg, f'{e}: {pp_args}') from e

    if len(pp_args_dict) == 1 and 'default' in pp_args_dict:
        # Return the default value if no keys were matched
        return tuple(pp_args_dict['default'])
    else:
        return {
            key: tuple(value) for key, value in pp_args_dict.items()
        }


def _parse_paths(args: YTDLOptHandlerArgs) -> dict[str, str]:
    """Convert --paths to a yt-dlp dict"""
    paths: list[str] = args.value
    paths_dict = parse_ytdlp_dicts(paths, default_key='home')

    return paths_dict


def _parse_extractor_args(
    args: YTDLOptHandlerArgs
) -> dict[str, dict[str, tuple[str, ...]]]:
    """Convert --extractor-args to a yt-dlp dict"""
    extractor_args: list[str] = args.value
    try:
        extractor_args_dict = parse_ytdlp_dicts(
            extractor_args, process=parse_extractor_arg
        )
    except ValueError as e:
        raise InvalidArgError(args.arg, f'{e}: {extractor_args}') from e

    return extractor_args_dict


def _set_writeinfojson(args: YTDLOptHandlerArgs) -> bool:
    """Ensure that 'writeinfojson' is `True` when --write-comments is
    given"""
    getcomments: bool = args.value

    if getcomments:
        logging.debug(
            'Implicitly setting write_info_json to True so that '
            'write_comments will work'
        )
        args.namespace.write_info_json = True

    return getcomments


# The actual return-type of this function should be
# `Union[bool, Literal[OMIT_OPT]]`, but Python doesn't support literal
# sentinel types.
# https://github.com/python/typing/issues/689
def _set_writelink(args: YTDLOptHandlerArgs) -> Any:
    """Set the write*link ytdl_opts based on the current platform"""
    writelink: bool = args.value

    if writelink:
        if sys.platform == 'win32':
            logging.debug(
                'Detected platform: Windows. Setting --write-url-link'
            )
            args.namespace.write_url_link = True
        elif sys.platform == 'darwin':
            logging.debug(
                'Detected platform: macOS. Setting --write-webloc-link'
            )
            args.namespace.write_webloc_link = True
        else:
            logging.debug(
                'Detected platform: Linux/Other. Setting --write-desktop-link'
            )
            args.namespace.write_desktop_link = True
        return OMIT_OPT
    else:
        args.namespace.write_url_link = False
        args.namespace.write_webloc_link = False
        args.namespace.write_desktop_link = False
        return False


def _split_format_sort(args: YTDLOptHandlerArgs) -> tuple[str, ...]:
    """Split the format_sort args into a list

    Whitespace is stripped and the args are appended in reverse in
    order to match the behavior of yt-dlp
    """
    unsplit: list[str] = args.value
    format_sort: list[str] = []

    for formats in reversed(unsplit):
        split = (format_.strip() for format_ in formats.split(','))
        format_sort += split

    return tuple(format_sort)


def _parse_outtmpl(args: YTDLOptHandlerArgs) -> Union[dict[str, str], str]:
    """Convert --output to a yt-dlp dict

    If no keys are matched, the value is returned by itself in order to
    remain backwards-compatible with youtube-dl
    """
    outtmpls: list[str] = args.value
    outtmpl_dict = parse_ytdlp_dicts(outtmpls, default_key='default')

    if len(outtmpl_dict) == 1 and 'default' in outtmpl_dict:
        # Return the value as-is if no keys were matched
        outtmpl: str = outtmpl_dict['default']
        return outtmpl
    else:
        return outtmpl_dict


def _pp_exec_cmd(args: YTDLOptHandlerArgs) -> dict[str, Any]:
    """Generate the --exec postprocessor

    When using yt-dlp, this is also supposed to have the 'when' key set
    to 'after_move', but this breaks compatibility with youtube-dl.
    The 'when' key defaults to 'post_process' when not given, so it will
    run a stage too early without it.

    Additionally, `exec_cmd` can be a list of commands when using
    yt-dlp, just like `exec_before_dl_cmd`, but that also breaks
    compatibility with youtube-dl.
    """
    exec_cmd: str = args.value
    return {
        'key': 'ExecAfterDownload',
        'exec_cmd': exec_cmd
    }


def _pp_exec_before_dl_cmd(args: YTDLOptHandlerArgs) -> dict[str, Any]:
    """Generate the --exec-before-download postprocessor"""
    exec_before_dl_cmd: list[str] = args.value
    return {
        'key': 'Exec',
        'exec_cmd': exec_before_dl_cmd,
        'when': 'before_dl'
    }


CUSTOM_OPTS = (
    CustomOpt(custom_opt='datebefore', args=('date', 'datebefore')),
    CustomOpt(custom_opt='dateafter', args=('date', 'dateafter')),
    CustomOpt(
        custom_opt='sponsorblock',
        args=('sponsorblock_mark', 'sponsorblock_remove', 'no_sponsorblock'),
        handler=_custom_sponsorblock
    ),
    CustomOpt(
        custom_opt='parse_metadata', args=('parse_metadata',),
        handler=_custom_parse_metadata
    ),
    CustomOpt(
        custom_opt='replace_in_metadata', args=('replace_in_metadata',),
        handler=_custom_replace_in_metadata
    ),
    CustomOpt(custom_opt='metafromtitle', args=('metadata_from_title',)),
    CustomOpt(custom_opt='convertsubtitles', args=('convert_subs',)),
    CustomOpt(custom_opt='convertthumbnails', args=('convert_thumbnails',)),
    CustomOpt(
        custom_opt='extractaudio', args=('extract_audio',),
        handler=_custom_extractaudio
    ),
    CustomOpt(
        custom_opt='remuxvideo', args=('remux_video',),
        handler=_custom_remuxvideo
    ),
    CustomOpt(
        custom_opt='recodevideo', args=('recode_video',),
        handler=_custom_recodevideo
    ),
    CustomOpt(custom_opt='embedsubtitles', args=('embed_subs',)),
    CustomOpt(
        custom_opt='remove_chapters', args=('remove_chapters',),
        handler=_custom_remove_chapters
    ),
    CustomOpt(custom_opt='addmetadata', args=('add_metadata',)),
    CustomOpt(custom_opt='addchapters', args=('embed_chapters',)),
    CustomOpt(custom_opt='embedthumbnail', args=('embed_thumbnail',)),
    CustomOpt(
        custom_opt='split_chapters', args=('split_chapters',),
        handler=_custom_split_chapters
    ),
    CustomOpt(custom_opt='xattrs', args=('xattrs',))
)
"""List of custom_opts and their corresponding argparse args

These will be used to generate the custom_opts dict when
`create.Create.from_argparse()` is used
"""


YTDL_OPTS = (
    # yt-dlp options
    YTDLOpt(ytdl_opt='break_on_existing'),
    YTDLOpt(ytdl_opt='break_on_reject'),
    YTDLOpt(ytdl_opt='skip_playlist_after_errors'),
    YTDLOpt(
        ytdl_opt='throttledratelimit', arg='throttled_rate',
        handler=_size_from_str
    ),
    YTDLOpt(ytdl_opt='paths', handler=_parse_paths),
    YTDLOpt(ytdl_opt='windowsfilenames', arg='windows_filenames'),
    YTDLOpt(ytdl_opt='trim_file_name', arg='trim_filenames'),
    # This is separate from nooverwrites because setting nooverwrites to
    # `None` doesn't do anything.
    # overwrites has priority over nooverwrites.
    YTDLOpt(ytdl_opt='overwrites', arg='no_force_overwrites'),
    YTDLOpt(ytdl_opt='allow_playlist_files', arg='write_playlist_metafiles'),
    YTDLOpt(ytdl_opt='clean_infojson'),
    YTDLOpt(
        ytdl_opt='getcomments', arg='write_comments',
        handler=_set_writeinfojson
    ),
    YTDLOpt(ytdl_opt='writelink', arg='write_link', handler=_set_writelink),
    YTDLOpt(ytdl_opt='writeurllink', arg='write_url_link'),
    YTDLOpt(ytdl_opt='writewebloclink', arg='write_webloc_link'),
    YTDLOpt(ytdl_opt='writedesktoplink', arg='write_desktop_link'),
    YTDLOpt(ytdl_opt='ignore_no_formats_error'),
    YTDLOpt(
        ytdl_opt='force_write_download_archive', arg='force_write_archive'
    ),
    YTDLOpt(ytdl_opt='sleep_interval_requests', arg='sleep_requests'),
    YTDLOpt(ytdl_opt='sleep_interval_subtitles', arg='sleep_subtitles'),
    YTDLOpt(ytdl_opt='format_sort', handler=_split_format_sort),
    YTDLOpt(ytdl_opt='format_sort_force'),
    YTDLOpt(ytdl_opt='allow_multiple_video_streams', arg='video_multistreams'),
    YTDLOpt(ytdl_opt='allow_multiple_audio_streams', arg='audio_multistreams'),
    YTDLOpt(ytdl_opt='check_formats'),
    YTDLOpt(ytdl_opt='extractor_retries', handler=_parse_retries),
    YTDLOpt(ytdl_opt='dynamic_mpd', arg='allow_dynamic_mpd'),
    YTDLOpt(ytdl_opt='hls_split_discontinuity'),
    YTDLOpt(ytdl_opt='extractor_args', handler=_parse_extractor_args),

    # youtube-dl options
    YTDLOpt(ytdl_opt='ignoreerrors', arg='ignore_errors'),
    YTDLOpt(ytdl_opt='force_generic_extractor'),
    YTDLOpt(ytdl_opt='default_search'),
    YTDLOpt(ytdl_opt='proxy'),
    YTDLOpt(ytdl_opt='socket_timeout'),
    YTDLOpt(ytdl_opt='source_address'),
    YTDLOpt(ytdl_opt='geo_verification_proxy'),
    YTDLOpt(ytdl_opt='geo_bypass'),
    YTDLOpt(ytdl_opt='geo_bypass_country'),
    YTDLOpt(ytdl_opt='geo_bypass_ip_block'),
    YTDLOpt(ytdl_opt='playliststart', arg='playlist_start'),
    YTDLOpt(
        ytdl_opt='playlistend', arg='playlist_end', handler=_check_playlistend
    ),
    YTDLOpt(ytdl_opt='playlist_items'),
    YTDLOpt(ytdl_opt='matchtitle', arg='match_title'),
    YTDLOpt(ytdl_opt='rejecttitle', arg='reject_title'),
    YTDLOpt(ytdl_opt='min_filesize', handler=_size_from_str),
    YTDLOpt(ytdl_opt='max_filesize', handler=_size_from_str),
    YTDLOpt(ytdl_opt='min_views'),
    YTDLOpt(ytdl_opt='max_views'),
    YTDLOpt(ytdl_opt='noplaylist', arg='no_playlist'),
    YTDLOpt(ytdl_opt='age_limit'),
    YTDLOpt(ytdl_opt='download_archive'),
    YTDLOpt(ytdl_opt='include_ads'),
    YTDLOpt(ytdl_opt='ratelimit', arg='limit_rate', handler=_size_from_str),
    YTDLOpt(ytdl_opt='retries', handler=_parse_retries),
    YTDLOpt(ytdl_opt='buffersize', arg='buffer_size', handler=_size_from_str),
    YTDLOpt(ytdl_opt='noresizebuffer', arg='no_resize_buffer'),
    YTDLOpt(ytdl_opt='http_chunk_size', handler=_size_from_str),
    YTDLOpt(ytdl_opt='playlistreverse', arg='playlist_reverse'),
    YTDLOpt(ytdl_opt='playlistrandom', arg='playlist_random'),
    YTDLOpt(ytdl_opt='xattr_set_filesize'),
    YTDLOpt(ytdl_opt='hls_prefer_native'),
    YTDLOpt(ytdl_opt='hls_use_mpegts'),
    YTDLOpt(ytdl_opt='external_downloader', handler=_parse_downloader),
    YTDLOpt(
        ytdl_opt='external_downloader_args', handler=_parse_downloader_args
    ),
    YTDLOpt(ytdl_opt='outtmpl', arg='output', handler=_parse_outtmpl),
    YTDLOpt(ytdl_opt='output_na_placeholder'),
    YTDLOpt(ytdl_opt='restrictfilenames', arg='restrict_filenames'),
    YTDLOpt(ytdl_opt='nooverwrites', arg='no_overwrites'),
    YTDLOpt(ytdl_opt='continuedl', arg='continue'),
    YTDLOpt(ytdl_opt='nopart', arg='no_part'),
    YTDLOpt(ytdl_opt='updatetime', arg='no_mtime', handler=_negate_bool),
    YTDLOpt(ytdl_opt='writedescription', arg='write_description'),
    YTDLOpt(ytdl_opt='writeinfojson', arg='write_info_json'),
    YTDLOpt(ytdl_opt='writeannotations', arg='write_annotations'),
    YTDLOpt(ytdl_opt='cookiefile', arg='cookies'),
    YTDLOpt(ytdl_opt='cachedir', arg='cache_dir'),
    YTDLOpt(ytdl_opt='writethumbnail', arg='write_thumbnail'),
    YTDLOpt(ytdl_opt='write_all_thumbnails'),
    YTDLOpt(ytdl_opt='simulate'),
    YTDLOpt(ytdl_opt='skip_download'),
    YTDLOpt(ytdl_opt='encoding'),
    YTDLOpt(ytdl_opt='nocheckcertificate', arg='no_check_certificate'),
    YTDLOpt(ytdl_opt='prefer_insecure'),
    YTDLOpt(ytdl_opt='sleep_interval'),
    YTDLOpt(ytdl_opt='max_sleep_interval', handler=_check_max_sleep_interval),
    YTDLOpt(ytdl_opt='format'),
    YTDLOpt(ytdl_opt='youtube_include_dash_manifest'),
    YTDLOpt(ytdl_opt='merge_output_format'),
    YTDLOpt(
        ytdl_opt='allsubtitles', arg='all_subs', handler=_set_writesubtitles
    ),
    YTDLOpt(ytdl_opt='writesubtitles', arg='write_sub'),
    YTDLOpt(ytdl_opt='writeautomaticsub', arg='write_auto_sub'),
    YTDLOpt(ytdl_opt='subtitlesformat', arg='sub_format'),
    YTDLOpt(ytdl_opt='subtitleslangs', arg='sub_lang'),
    YTDLOpt(ytdl_opt='username', handler=_check_username),
    YTDLOpt(ytdl_opt='password', handler=_check_password),
    YTDLOpt(ytdl_opt='usenetrc', arg='netrc'),
    YTDLOpt(ytdl_opt='videopassword', arg='video_password'),
    YTDLOpt(ytdl_opt='ap_mso'),
    YTDLOpt(ytdl_opt='ap_username', handler=_check_ap_username),
    YTDLOpt(ytdl_opt='ap_password', handler=_check_ap_password),
    YTDLOpt(ytdl_opt='postprocessor_args', handler=_parse_ppa),
    YTDLOpt(ytdl_opt='keepvideo', arg='keep_video'),
    YTDLOpt(ytdl_opt='fixup'),
    YTDLOpt(ytdl_opt='prefer_ffmpeg'),
    YTDLOpt(ytdl_opt='ffmpeg_location')
)
"""List of ytdl_opts and their corresponding argparse arg

These will be used to generate the ytdl_opts dict when
`create.Create.from_argparse()` is used
"""

POSTPROCESSOR_OPTS = (
    PostProcessorOpt(
        arg='exec_before_download', handler=_pp_exec_before_dl_cmd
    ),
    PostProcessorOpt(arg='exec', handler=_pp_exec_cmd)
)
"""List of postprocessor args

These will be added to the 'postprocessors' list in the ytdl_opts, in
order
"""
