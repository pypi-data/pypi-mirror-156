"""argparse parser"""

from __future__ import annotations

__all__ = ('get_parser',)

import argparse
import uuid
from typing import TYPE_CHECKING

from . import __version__ as _version
from .util import MAX_NUMBER

if TYPE_CHECKING:
    from typing import TypeVar

    NumT = TypeVar('NumT', int, float)


def _number_min(type_: type[NumT], min_: NumT, arg: str) -> NumT:
    number = type_(arg)
    max_number = type_(MAX_NUMBER)

    if number < min_:
        raise argparse.ArgumentTypeError(
            f'value must be at least {min_}: {arg}'
        )
    return min(number, max_number)


def _number_range(type_: type[NumT], min_: NumT, max_: NumT, arg: str) -> NumT:
    number = type_(arg)

    if number < min_:
        raise argparse.ArgumentTypeError(
            f'value must be at least {min_}: {arg}'
        )
    elif number > max_:
        raise argparse.ArgumentTypeError(
            f'value must be no more than {max_}: {arg}'
        )
    return number


def _positive_int(arg: str) -> int:
    """Type function for argparse that asserts that the value is a
    positive integer (including 0).

    The value is capped at the max JSON number.
    """
    return _number_min(int, 0, arg)


def _positive_float(arg: str) -> float:
    """Type function for argparse that asserts that the value is a
    positive float (including 0)

    The value is capped at the max JSON number.
    """
    return _number_min(float, 0, arg)


def _int_ge_neg1(arg: str) -> int:
    """Type function for argparse that asserts that the value is an
    int >= -1

    The value is capped at the max JSON number.
    """
    return _number_min(int, -1, arg)


def _float_0_to_1(arg: str) -> float:
    """Type function for argparse that asserts that the value is a
    float between 0 and 1, inclusive."""
    return _number_range(float, 0, 1, arg)


def _comma_separated_list(arg: str) -> tuple[str, ...]:
    """Type function for argparse that converts a comma-separated list

    Also strips whitespace from each item
    """
    return tuple(s.strip() for s in arg.split(','))


def _audioquality(audioquality: str) -> int:
    """Type function for the --audio-quality arg

    --audio-quality must be an integer >= 0.

    It can also optionally end with 'k' or 'K', which is stripped from
    the final value
    """
    if audioquality.endswith(('k', 'K'),):
        audioquality = audioquality[:-1]

    return _positive_int(audioquality)


def get_parser() -> argparse.ArgumentParser:
    """Creates the ArgumentParser used by `cli.main()`"""
    parser = argparse.ArgumentParser(
        description='Command-line frontend for ytdl-server'
    )
    parser.add_argument('--version', action='version', version=_version)
    parser.add_argument(
        '-s', '--ytdl-server', metavar='URL',
        help=(
            'The ytdl-server REST API to connect to. This can also be given '
            'via the $YTDL_SERVER env-var.'
        )
    )
    parser.add_argument(
        '-u', '--ytdl-username', metavar='USER',
        help=(
            'Username to use when connecting to the ytdl-server if the server '
            'uses basic authentication. This can also be given via the '
            '$YTDL_SERVER_USERNAME env-var.'
        )
    )
    parser.add_argument(
        '-p', '--ytdl-password', metavar='PASSWD',
        help=(
            'Password to use when connecting to the ytdl-server if the server '
            'uses basic authentication. This can also be given via the '
            '$YTDL_SERVER_PASSWORD env-var. If this option is left out when '
            '--ytdl-username is given, ytcl will ask interactively.'
        )
    )
    parser.add_argument(
        '-d', '--detach', action='store_true',
        help="Don't wait for the job to finish before exiting."
    )
    parser.add_argument(
        '-i', '--interval', type=_positive_float, metavar='SECONDS',
        default=1.0,
        help=(
            'How frequently to poll the ytdl-server for status updates when '
            'waiting for a job to finish (default: %(default)s).'
        )
    )
    parser.add_argument(
        '-f', '--output-format', choices=('progress', 'all', 'json'),
        default='progress',
        help=(
            'Output format to use. '
            "If 'progress', download progress and logs will be printed. "
            "If 'all', all information about the job will be printed in a "
            'human-readable format. '
            "If 'json', all information about the job will be printed as "
            'JSON. '
            '(default: %(default)s)'
        )
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='Print debug information. Conflicts with --quiet.'
    )
    parser.add_argument(
        '-q', '--quiet', action='store_true',
        help='Only print errors. Conflicts with --verbose.'
    )
    parser.add_argument(
        '--color', choices=('always', 'auto', 'never'), default='auto',
        help=(
            'Whether or not to colorize the output using ANSI escape codes. '
            "If 'auto', color will be enabled if stdout is a TTY "
            '(default: %(default)s).'
        )
    )
    parser.add_argument(
        '--progress-format', choices=('auto', 'overwrite', 'new_line', 'none'),
        default='auto',
        help=(
            'Download progress format. '
            "If 'overwrite', the progress will be overwritten so that only "
            'a single line is visible at a time. '
            "If 'new_line', each update will be printed as a new line. "
            "If 'none', no progress information will be printed. "
            "If 'auto', 'overwrite' will be used if stdout is a TTY; "
            "otherwise 'new_line' will be used. "
            'This only has an effect when --output-format=progress '
            '(default: %(default)s).'
        )
    )
    parser.add_argument(
        '--speed-ema-weight', type=_float_0_to_1, metavar='WEIGHT',
        default=0.2,
        help=(
            'Weight constant used to calculate the exponential moving average '
            '(EMA) of the download speed. This is used to smooth out the '
            "reported download speed so that it doesn't constantly fluctuate "
            'when downloading fragmented files. Must be between 0 and 1, '
            'inclusive. A higher value means that more weight will be put on '
            "the current download speed. Set to '1' to always display the "
            'current speed (default: %(default)s).'
        )
    )
    subparsers = parser.add_subparsers(dest='subparser', required=True)

    get_parser = subparsers.add_parser(
        'get', help='Get the status of a job.'
    )
    get_parser.add_argument(
        'job_id', type=uuid.UUID, help='The job ID to query.'
    )
    get_parser.add_argument(
        '-l', '--log-lines', type=_positive_int, default=4,
        help=(
            'Number of old log entries to initially print when '
            "--output-format=progress. Set to '0' to print all logs "
            '(default: %(default)s).'
        )
    )

    create_parser = subparsers.add_parser(
        'create', help='create a new job', argument_default=argparse.SUPPRESS,
        usage='%(prog)s [options] [url ...]', add_help=False
    )
    _add_create_args(create_parser)

    cancel_parser = subparsers.add_parser(
        'cancel', help='Cancel a running job.'
    )
    cancel_parser.add_argument(
        'job_id', type=uuid.UUID, help='The job ID to cancel.'
    )

    return parser


def _add_create_args(parser: argparse.ArgumentParser) -> None:
    """Add the arguments for the create subparser

    The parser *must* be created with the kwargs
    `argument_default=argparse.SUPPRESS` and `add_help=False`
    """
    # 'url' is optional because the user can also supply URLs via
    # '--batch-file'
    parser.add_argument(
        'url', nargs='*', default=(), help='List of video URLs to download.'
    )

    ytcl_group = parser.add_argument_group(
        'ytcl options',
        description='Options that change the client-side behavior of ytcl.'
    )
    ytdl_group = parser.add_argument_group('youtube-dl options')
    ytdl_default_group = parser.add_argument_group(
        'default youtube-dl options',
        description=(
            'Default behavior when using youtube-dl on the command-line. You '
            "don't need to use these unless the ytdl-server has a custom "
            'default config.'
        )
    )
    ytdlp_group = parser.add_argument_group(
        'yt-dlp options',
        description=(
            'Options that only work when the ytdl-server is using yt-dlp.'
        )
    )
    ytdlp_default_group = parser.add_argument_group(
        'default yt-dlp options',
        description=(
            'Default behavior when using yt-dlp on the command-line. You '
            "don't need to use these unless the ytdl-server has a custom "
            'default config.'
        )
    )

    ytcl_group.add_argument(
        '-h', '--help', action='help', help='Show this help message and exit.'
    )
    # Alias for --verbose in the parent parser
    ytcl_group.add_argument(
        '-v', '--verbose', action='store_true',
        help='Print debug information.'
    )
    # Alias for --quiet in the parent parser
    ytcl_group.add_argument(
        '-q', '--quiet', action='store_true',
        help='Only print errors. Conflicts with --verbose.'
    )
    # Alias for --color=never in the parent parser
    ytcl_group.add_argument(
        '--no-color', '--no-colors', action='store_const', const='never',
        dest='color',
        help=(
            'Do not colorize the output using ANSI escape codes. '
            'Equivalent to --color=never.'
        )
    )
    # Alias for --progress-format=new_line in the parent parser
    ytcl_group.add_argument(
        '--newline', action='store_const', const='new_line',
        dest='progress_format',
        help=(
            'Output the download progress information as new lines. '
            'Equivalent to --progress-format=new_line.'
        )
    )
    # Alias for --progress-format=none in the parent parser
    ytcl_group.add_argument(
        '--no-progress', action='store_const', const='none',
        dest='progress_format',
        help=(
            'Do not print download progress. Equivalent to '
            '--progress-format=none.'
        )
    )

    ytdl_group.add_argument(
        '-i', '--ignore-errors', action='store_true',
        help=(
            'Continue on download errors, for example to skip unavailable '
            'videos in a playlist'
        )
    )
    ytdl_default_group.add_argument(
        '--abort-on-error', '--no-ignore-errors', action='store_false',
        dest='ignore_errors',
        help='Do not continue on download errors. Inverse of --ignore-errors'
    )
    ytdl_group.add_argument(
        '--force-generic-extractor', action='store_true',
        help='Force extraction to use the generic extractor'
    )
    ytdl_default_group.add_argument(
        '--no-force-generic-extractor', action='store_false',
        dest='force_generic_extractor',
        help='Inverse of --force-generic-extractor'
    )
    ytdl_group.add_argument(
        '--default-search', metavar='PREFIX',
        help=(
            'Use this prefix for unqualified URLs. For example "gvsearch2:" '
            'downloads two videos from google videos for youtube-dl '
            '"large apple". Use the value "auto" to let youtube-dl guess '
            '("auto_warning" to emit a warning when guessing). "error" just '
            'throws an error. "fixup_error" repairs broken URLs, but emits an '
            'error if this is not possible instead of searching.'
        )
    )
    ytdl_group.add_argument(
        '--proxy', metavar='URL',
        help=(
            'Use the specified HTTP/HTTPS/SOCKS proxy. To enable SOCKS proxy, '
            'specify a proper scheme. For example socks5://127.0.0.1:1080/. '
            'Pass in an empty string (--proxy "") for direct connection'
        )
    )
    ytdl_group.add_argument(
        '--socket-timeout', type=_positive_float, metavar='SECONDS',
        help='Time to wait before giving up, in seconds'
    )
    ytdl_group.add_argument(
        '--source-address', metavar='IP',
        help='Client-side IP address to bind to'
    )
    ytdl_group.add_argument(
        '-4', '--force-ipv4', dest='source_address', action='store_const',
        const='0.0.0.0',
        help='Make all connections via IPv4'
    )
    ytdl_group.add_argument(
        '-6', '--force-ipv6', dest='source_address', action='store_const',
        const='::',
        help='Make all connections via IPv6'
    )
    ytdl_group.add_argument(
        '--geo-verification-proxy', metavar='URL',
        help=(
            'Use this proxy to verify the IP address for some geo-restricted '
            'sites. The default proxy specified by --proxy (or none, if the '
            'option is not present) is used for the actual downloading.'
        )
    )
    ytdl_default_group.add_argument(
        '--geo-bypass', action='store_true',
        help=(
            'Bypass geographic restriction via faking X-Forwarded-For HTTP '
            'header. Inverse of --no-geo-bypass.'
        )
    )
    ytdl_group.add_argument(
        '--no-geo-bypass', action='store_false', dest='geo_bypass',
        help='Do not bypass geographic restriction.'
    )
    ytdl_group.add_argument(
        '--geo-bypass-country', metavar='CODE',
        help=(
            'Force bypass geographic restriction with explicitly provided '
            'two-letter ISO 3166-2 country code'
        )
    )
    ytdl_group.add_argument(
        '--geo-bypass-ip-block', metavar='IP_BLOCK',
        help=(
            'Force bypass geographic restriction with explicitly provided IP '
            'block in CIDR notation'
        )
    )
    ytdl_group.add_argument(
        '--playlist-start', type=_positive_int, metavar='NUMBER',
        help='Playlist video to start at'
    )
    # --playlist-end can be `-1`, which is equivalent to `None`
    ytdl_group.add_argument(
        '--playlist-end', type=_int_ge_neg1, metavar='NUMBER',
        help='Playlist video to end at'
    )
    ytdl_group.add_argument(
        '--playlist-items', metavar='ITEM_SPEC',
        help=(
            'Playlist video items to download. Specify indices of the videos '
            'in the playlist separated by commas like: '
            '"--playlist-items 1,2,5,8" if you want to download videos '
            'indexed 1, 2, 5, 8 in the playlist. You can specify range: '
            '"--playlist-items 1-3,7,10-13", it will download the videos at '
            'index 1, 2, 3, 7, 10, 11, 12 and 13.'
        )
    )
    ytdl_group.add_argument(
        '--match-title', metavar='REGEX',
        help='Download only matching titles (regex or caseless sub-string)'
    )
    ytdl_group.add_argument(
        '--reject-title', metavar='REGEX',
        help='Skip download for matching titles (regex or caseless sub-string)'
    )
    ytdl_group.add_argument(
        '--min-filesize', metavar='SIZE',
        help='Do not download any videos smaller than SIZE (e.g. 50k or 44.6m)'
    )
    ytdl_group.add_argument(
        '--max-filesize', metavar='SIZE',
        help='Do not download any videos larger than SIZE (e.g. 50k or 44.6m)'
    )
    ytdl_group.add_argument(
        '--date', metavar='DATE',
        help='Download only videos uploaded in this date'
    )
    ytdl_group.add_argument(
        '--datebefore', metavar='DATE',
        help=(
            'Download only videos uploaded on or before this date '
            '(i.e. inclusive)'
        )
    )
    ytdl_group.add_argument(
        '--dateafter', metavar='DATE',
        help=(
            'Download only videos uploaded on or after this date '
            '(i.e. inclusive)'
        )
    )
    ytdl_group.add_argument(
        '--min-views', type=_positive_int, metavar='COUNT',
        help='Do not download any videos with less than COUNT views'
    )
    ytdl_group.add_argument(
        '--max-views', type=_positive_int, metavar='COUNT',
        help='Do not download any videos with more than COUNT views'
    )
    ytdl_group.add_argument(
        '--no-playlist', action='store_true',
        help=(
            'Download only the video, if the URL refers to a video and a '
            'playlist.'
        )
    )
    ytdl_default_group.add_argument(
        '--yes-playlist', action='store_false', dest='no_playlist',
        help=(
            'Download the playlist, if the URL refers to a video and a '
            'playlist. Inverse of --no-playlist.'
        )
    )
    ytdl_group.add_argument(
        '--age-limit', type=_positive_int, metavar='YEARS',
        help='Download only videos suitable for the given age'
    )
    ytdl_group.add_argument(
        '--download-archive', metavar='FILE',
        help=(
            'Download only videos not listed in the archive file. Record the '
            'IDs of all downloaded videos in it.'
        )
    )
    ytdl_default_group.add_argument(
        '--no-download-archive', action='store_const', const=None,
        dest='download_archive',
        help='Inverse of --download-archive'
    )
    ytdl_group.add_argument(
        '--include-ads', action='store_true',
        help='Download advertisements as well (experimental)'
    )
    ytdl_default_group.add_argument(
        '--no-include-ads', action='store_false', dest='include_ads',
        help='Inverse of --include-ads'
    )
    ytdl_group.add_argument(
        '-r', '--limit-rate', '--rate-limit', metavar='RATE',
        help='Maximum download rate per second, in bytes (e.g. 50K or 4.2M)'
    )
    ytdl_group.add_argument(
        '-R', '--retries', metavar='RETRIES',
        help='Number of retries, or "infinite"'
    )
    ytdl_group.add_argument(
        '--buffer-size', metavar='SIZE',
        help='Size of download buffer (e.g. 1024 or 16K)'
    )
    ytdl_group.add_argument(
        '--no-resize-buffer', action='store_true',
        help='Do not automatically adjust the buffer size'
    )
    ytdl_default_group.add_argument(
        '--resize-buffer', action='store_false', dest='no_resize_buffer',
        help='Inverse of --no-resize-buffer'
    )
    ytdl_group.add_argument(
        '--http-chunk-size', metavar='SIZE',
        help=(
            'Size of a chunk for chunk-based HTTP downloading '
            '(e.g. 10485760 or 10M). May be useful for bypassing bandwidth '
            'throttling imposed by a webserver (experimental)'
        )
    )
    ytdl_group.add_argument(
        '--playlist-reverse', action='store_true',
        help='Download playlist videos in reverse order'
    )
    ytdl_default_group.add_argument(
        '--no-playlist-reverse', action='store_false', dest='playlist_reverse',
        help='Inverse of --playlist-reverse'
    )
    ytdl_group.add_argument(
        '--playlist-random', action='store_true',
        help='Download playlist videos in random order'
    )
    ytdl_default_group.add_argument(
        '--no-playlist-random', action='store_false', dest='playlist_random',
        help='Inverse of --playlist-random'
    )
    ytdl_group.add_argument(
        '--xattr-set-filesize', action='store_true',
        help='Set file xattribute ytdl.filesize with expected file size'
    )
    ytdl_default_group.add_argument(
        '--no-xattr-set-filesize', action='store_false',
        dest='xattr_set_filesize',
        help='Inverse of --xattr-set-filesize'
    )
    ytdl_group.add_argument(
        '--hls-prefer-native', action='store_true',
        help='Use the native HLS downloader instead of ffmpeg'
    )
    ytdl_default_group.add_argument(
        '--hls-prefer-ffmpeg', action='store_false', dest='hls_prefer_native',
        help=(
            'Use ffmpeg instead of the native HLS downloader. Inverse of '
            '--hls-prefer-native.'
        )
    )
    ytdl_group.add_argument(
        '--hls-use-mpegts', action='store_true',
        help=(
            'Use the mpegts container for HLS videos, allowing to play the '
            'video while downloading (some players may not be able to play it)'
        )
    )
    ytdl_default_group.add_argument(
        '--no-hls-use-mpegts', action='store_false', dest='hls_use_mpegts',
        help='Inverse of --hls-use-mpegts'
    )
    ytdl_group.add_argument(
        '--external-downloader', '--downloader', metavar='[PROTO:]COMMAND',
        action='append',
        help=(
            'Use the specified external downloader. The PROTO:COMMAND syntax '
            'is supported only if the ytdl-server is using yt-dlp.'
        )
    )
    ytdl_group.add_argument(
        '--external-downloader-args', '--downloader-args',
        metavar='[NAME:]ARGS', action='append',
        help=(
            'Give these arguments to the external downloader. The NAME:ARGS '
            'syntax is supported only if the ytdl-server is using yt-dlp.'
        )
    )
    ytdl_group.add_argument(
        '-a', '--batch-file', type=argparse.FileType('r'), metavar='FILE',
        help=(
            "File containing URLs to download ('-' for stdin), one URL per "
            "line. Lines starting with '#', ';' or ']' are considered as "
            'comments and ignored.'
        )
    )
    ytdl_group.add_argument(
        '--id', action='store_const', const='%(id)s.%(ext)s', dest='output',
        help='Use only video ID in file name. Equivalent to --output=%(const)r'
    )
    ytdl_group.add_argument(
        '-o', '--output', metavar='[TYPES:]TEMPLATE', action='append',
        help=(
            'Output filename template. The TYPES:TEMPLATE syntax is supported '
            'only if the ytdl-server is using yt-dlp.'
        )
    )
    ytdl_group.add_argument(
        '--output-na-placeholder', metavar='PLACEHOLDER',
        help=(
            'Placeholder value for unavailable meta fields in output filename '
            'template'
        )
    )
    ytdl_group.add_argument(
        '--restrict-filenames', action='store_true',
        help=(
            'Restrict filenames to only ASCII characters, and avoid "&" and '
            'spaces in filenames'
        )
    )
    ytdl_default_group.add_argument(
        '--no-restrict-filenames', action='store_false',
        dest='restrict_filenames',
        help='Inverse of --restrict-filenames'
    )
    ytdl_group.add_argument(
        '-w', '--no-overwrites', action='store_true',
        help='Do not overwrite files'
    )
    ytdl_default_group.add_argument(
        '--overwrites', '--force-overwrites', '--yes-overwrites',
        action='store_false', dest='no_overwrites',
        help=(
            'Inverse of --no-overwrites. Note that unlike yt-dlp, this does '
            'NOT imply --no-continue.'
        )
    )
    ytdl_default_group.add_argument(
        '-c', '--continue', action='store_true',
        help=(
            'Force resume of partially downloaded files. Inverse of '
            '--no-continue.'
        )
    )
    ytdl_group.add_argument(
        '--no-continue', action='store_false', dest='continue',
        help=(
            'Do not resume partially downloaded files '
            '(restart from beginning).'
        )
    )
    ytdl_group.add_argument(
        '--no-part', action='store_true',
        help='Do not use .part files - write directly into output file'
    )
    ytdl_default_group.add_argument(
        '--part', action='store_false', dest='no_part',
        help='Inverse of --no-part'
    )
    ytdl_group.add_argument(
        '--no-mtime', action='store_true',
        help=(
            'Do not use the Last-modified header to set the file modification '
            'time'
        )
    )
    ytdl_default_group.add_argument(
        '--mtime', action='store_false', dest='no_mtime',
        help='Inverse of --no-mtime'
    )
    ytdl_group.add_argument(
        '--write-description', action='store_true',
        help='Write video description to a .description file'
    )
    ytdl_default_group.add_argument(
        '--no-write-description', action='store_false',
        dest='write_description',
        help='Inverse of --write-description'
    )
    ytdl_group.add_argument(
        '--write-info-json', action='store_true',
        help='Write video metadata to a .info.json file'
    )
    ytdl_default_group.add_argument(
        '--no-write-info-json', action='store_false', dest='write_info_json',
        help='Inverse of --write-info-json'
    )
    ytdl_group.add_argument(
        '--write-annotations', action='store_true',
        help='Write video annotations to a .annotations.xml file'
    )
    ytdl_default_group.add_argument(
        '--no-write-annotations', action='store_false',
        dest='write_annotations',
        help='Inverse of --write-annotations'
    )
    ytdl_group.add_argument(
        '--cookies', metavar='FILE',
        help=(
            'File to read cookies from and dump cookie jar in. The file must '
            'be accessible by the ytdl-server worker'
        )
    )
    ytdl_default_group.add_argument(
        '--no-cookies', action='store_const', const=None, dest='cookies',
        help='Inverse of --cookies'
    )
    ytdl_group.add_argument(
        '--cache-dir', metavar='DIR',
        help=(
            'Location in the filesystem where youtube-dl can store some '
            'downloaded information permanently. The dir must be accessible '
            'by the ytdl-server worker'
        )
    )
    ytdl_group.add_argument(
        '--no-cache-dir', action='store_false', dest='cache_dir',
        help='Disable filesystem caching. Inverse of --cache-dir'
    )
    ytdl_group.add_argument(
        '--write-thumbnail', action='store_true',
        help='Write thumbnail image to disk'
    )
    ytdl_default_group.add_argument(
        '--no-write-thumbnail', action='store_false', dest='write_thumbnail',
        help='Inverse of --write-thumbnail'
    )
    ytdl_group.add_argument(
        '--write-all-thumbnails', action='store_true',
        help='Write all thumbnail image formats to disk'
    )
    ytdl_default_group.add_argument(
        '--no-write-all-thumbnails', action='store_false',
        dest='write_all_thumbnails',
        help='Inverse of --write-all-thumbnails'
    )
    ytdl_group.add_argument(
        '-s', '--simulate', action='store_true',
        help='Do not download the video and do not write anything to disk'
    )
    ytdl_default_group.add_argument(
        '--no-simulate', action='store_false', dest='simulate',
        help='Inverse of --simulate'
    )
    ytdl_group.add_argument(
        '--skip-download', action='store_true',
        help='Do not download the video'
    )
    ytdl_default_group.add_argument(
        '--no-skip-download', action='store_false', dest='skip_download',
        help='Inverse of --skip-download'
    )
    ytdl_group.add_argument(
        '--encoding', metavar='ENCODING',
        help='Force the specified encoding (experimental)'
    )
    ytdl_group.add_argument(
        '--no-check-certificate', action='store_true',
        help='Suppress HTTPS certificate validation'
    )
    ytdl_default_group.add_argument(
        '--check-certificate', action='store_false',
        dest='no_check_certificate',
        help='Inverse of --no-check-certificate'
    )
    ytdl_group.add_argument(
        '--prefer-insecure', '--prefer-unsecure', action='store_true',
        help=(
            'Use an unencrypted connection to retrieve information about '
            'the video'
        )
    )
    ytdl_default_group.add_argument(
        '--no-prefer-insecure', '--no-prefer-unsecure', action='store_false',
        dest='prefer_insecure',
        help='Inverse of --prefer-insecure / --prefer-unsecure'
    )
    ytdl_group.add_argument(
        '--sleep-interval', '--min-sleep-interval', type=_positive_float,
        metavar='SECONDS',
        help=(
            'Number of seconds to sleep before each download when used alone '
            'or a lower bound of a range for randomized sleep before each '
            'download (minimum possible number of seconds to sleep) when used '
            'along with --max-sleep-interval.'
        )
    )
    ytdl_group.add_argument(
        '--max-sleep-interval', type=_positive_float, metavar='SECONDS',
        help=(
            'Upper bound of a range for randomized sleep before each download '
            '(maximum possible number of seconds to sleep). Must only be used '
            'along with --min-sleep-interval.'
        )
    )
    ytdl_group.add_argument(
        '-f', '--format', metavar='FORMAT',
        help='Video format code'
    )
    ytdl_group.add_argument(
        '--all-formats', dest='format', action='store_const', const='all',
        help=(
            'Download all available video formats. Equivalent to '
            '--format=%(const)s'
        )
    )
    ytdl_default_group.add_argument(
        '--youtube-include-dash-manifest', action='store_true',
        help=(
            'Try to download the DASH manifest on YouTube videos. Inverse of '
            '--youtube-skip-dash-manifest.'
        )
    )
    ytdl_group.add_argument(
        '--youtube-skip-dash-manifest', action='store_false',
        dest='youtube_include_dash_manifest',
        help=(
            'Do not download the DASH manifests and related data on YouTube '
            'videos.'
        )
    )
    ytdl_group.add_argument(
        '--merge-output-format', metavar='FORMAT',
        help=(
            'If a merge is required (e.g. bestvideo+bestaudio), output to '
            'given container format. Ignored if no merge is required'
        )
    )
    ytdl_group.add_argument(
        '--write-sub', '--write-subs', '--write-srt', action='store_true',
        help='Write subtitle file'
    )
    ytdl_default_group.add_argument(
        '--no-write-sub', '--no-write-subs', '--no-write-srt',
        action='store_false', dest='write_sub',
        help='Inverse of --write-sub.'
    )
    ytdl_group.add_argument(
        '--write-auto-sub', '--write-automatic-sub', '--write-auto-subs',
        '--write-automatic-subs', action='store_true',
        help='Write automatically generated subtitle file (YouTube only)'
    )
    ytdl_default_group.add_argument(
        '--no-write-auto-sub', '--no-write-automatic-sub',
        '--no-write-auto-subs', '--no-write-automatic-subs',
        action='store_false', dest='write_auto_sub',
        help='Inverse of --write-auto-sub.'
    )
    ytdl_group.add_argument(
        '--all-subs', action='store_true',
        help='Download all the available subtitles of the video'
    )
    ytdl_default_group.add_argument(
        '--no-all-subs', action='store_false', dest='all_subs',
        help='Inverse of --all-subs'
    )
    ytdl_group.add_argument(
        '--sub-format', metavar='FORMAT',
        help=(
            'Subtitle format, accepts formats preference, for example: "srt" '
            'or "ass/srt/best"'
        )
    )
    ytdl_group.add_argument(
        '--sub-lang', '--sub-langs', '--srt-lang', metavar='LANGS',
        type=_comma_separated_list,
        help='Languages of the subtitles to download, separated by commas'
    )
    ytdl_group.add_argument(
        '-u', '--username',
        help='Login with this account ID'
    )
    ytdl_group.add_argument(
        '-p', '--password',
        help=(
            'Account password. If this option is left out, ytcl will ask '
            'interactively.'
        )
    )
    ytdl_group.add_argument(
        '-n', '--netrc', action='store_true',
        help='Use .netrc authentication data'
    )
    ytdl_default_group.add_argument(
        '--no-netrc', action='store_false', dest='netrc',
        help='Inverse of --netrc'
    )
    ytdl_group.add_argument(
        '--video-password', metavar='PASSWORD',
        help='Video password (vimeo, youku)'
    )
    ytdl_group.add_argument(
        '--ap-mso', metavar='MSO',
        help='Adobe Pass multiple-system operator (TV provider) identifier'
    )
    ytdl_group.add_argument(
        '--ap-username', metavar='USERNAME',
        help='Multiple-system operator account login'
    )
    ytdl_group.add_argument(
        '--ap-password', metavar='PASSWORD',
        help=(
            'Multiple-system operator account password. If this option is '
            'left out, ytcl will ask interactively.'
        )
    )
    ytdl_group.add_argument(
        '-x', '--extract-audio', action='store_true',
        help='Convert video files to audio-only files'
    )
    ytdl_default_group.add_argument(
        '--no-extract-audio', action='store_false', dest='extract_audio',
        help='Inverse of --extract-audio.'
    )
    ytdl_group.add_argument(
        '--audio-format', metavar='FORMAT', default='best',
        help=(
            'The audio format to use for --extract-audio '
            '(default: %(default)s)'
        )
    )
    ytdl_group.add_argument(
        '--audio-quality', metavar='QUALITY', default=5, type=_audioquality,
        help=(
            'The audio quality to use with --extract-audio. Insert a value '
            'between 0 (better) and 9 (worse) for VBR or a specific bitrate '
            'like 128K (default: %(default)s)'
        )
    )
    ytdl_group.add_argument(
        '--recode-video', metavar='FORMAT',
        help='Encode the video to another format if necessary'
    )
    ytdl_default_group.add_argument(
        '--no-recode-video', action='store_const', const=None,
        dest='recode_video',
        help='Inverse of --recode-video.'
    )
    ytdl_group.add_argument(
        '--postprocessor-args', '--ppa', metavar='[NAME:]ARGS',
        action='append',
        help=(
            'Give these arguments to the postprocessor. The NAME:ARGS syntax '
            'is supported only if the ytdl-server is using yt-dlp.'
        )
    )
    ytdl_group.add_argument(
        '-k', '--keep-video', action='store_true',
        help='Keep the video file on disk after the post-processing'
    )
    ytdl_default_group.add_argument(
        '--no-keep-video', action='store_false', dest='keep_video',
        help='Inverse of --keep-video'
    )
    ytdl_group.add_argument(
        '--no-post-overwrites', action='store_true', default=False,
        help=(
            'Do not overwrite post-processed files; the post-processed files '
            'are overwritten by default'
        )
    )
    ytdl_default_group.add_argument(
        '--post-overwrites', action='store_false', dest='no_post_overwrites',
        help='Inverse of --no-post-overwrites.'
    )
    ytdl_group.add_argument(
        '--embed-subs', action='store_true',
        help='Embed subtitles in the video'
    )
    ytdl_default_group.add_argument(
        '--no-embed-subs', action='store_false', dest='embed_subs',
        help='Inverse of --embed-subs.'
    )
    ytdl_group.add_argument(
        '--embed-thumbnail', action='store_true',
        help='Embed thumbnail in the audio as cover art'
    )
    ytdl_default_group.add_argument(
        '--no-embed-thumbnail', action='store_false', dest='embed_thumbnail',
        help='Inverse of --embed-thumbnail.'
    )
    ytdl_group.add_argument(
        '--add-metadata', '--embed-metadata', action='store_true',
        help='Write metadata to the video file'
    )
    ytdl_default_group.add_argument(
        '--no-add-metadata', '--no-embed-metadata', action='store_false',
        dest='add_metadata',
        help='Inverse of --add-metadata.'
    )
    ytdl_group.add_argument(
        '--metadata-from-title', metavar='FORMAT',
        help=(
            'Parse additional metadata like song title / artist from the '
            'video title. The format syntax is the same as --output. Regular '
            'expression with named capture groups may also be used. The '
            'parsed parameters replace existing values. Example: '
            '--metadata-from-title "%%(artist)s - %%(title)s" matches a title '
            'like "Coldplay - Paradise". Example (regex): '
            '--metadata-from-title "(?P<artist>.+?) - (?P<title>.+)"'
        )
    )
    ytdl_default_group.add_argument(
        '--no-metadata-from-title', action='store_const', const=None,
        dest='metadata_from_title',
        help='Inverse of --metadata-from-title.'
    )
    ytdl_group.add_argument(
        '--xattrs', action='store_true',
        help=(
            'Write metadata to the video file\'s xattrs (using dublin core '
            'and xdg standards)'
        )
    )
    ytdl_default_group.add_argument(
        '--no-xattrs', action='store_false', dest='xattrs',
        help='Inverse of --xattrs.'
    )
    ytdl_group.add_argument(
        '--fixup', choices=('never', 'warn', 'detect_or_warn'),
        help=(
            'Automatically correct known faults of the file. One of never '
            '(do nothing), warn (only emit a warning), detect_or_warn '
            '(fix file if we can, warn otherwise)'
        )
    )
    ytdl_default_group.add_argument(
        '--prefer-ffmpeg', action='store_true',
        help=(
            'Prefer ffmpeg over avconv for running the postprocessors. '
            'Inverse of --prefer-ffmpeg.'
        )
    )
    ytdl_group.add_argument(
        '--prefer-avconv', action='store_false', dest='prefer_ffmpeg',
        help='Prefer avconv over ffmpeg for running the postprocessors.'
    )
    ytdl_group.add_argument(
        '--ffmpeg-location', '--avconv-location', metavar='PATH',
        help=(
            'Location of the ffmpeg/avconv binary; either the path to the '
            'binary or its containing directory.'
        )
    )
    ytdl_group.add_argument(
        '--exec', metavar='CMD',
        help=(
            'Execute a command on the file after downloading and '
            'post-processing, similar to find\'s -exec syntax. Example: '
            '--exec \'adb push {} /sdcard/Music/ && rm {}\''
        )
    )
    ytdl_group.add_argument(
        '--convert-subs', '--convert-sub', '--convert-subtitles',
        metavar='FORMAT',
        help='Convert the subtitles to other format'
    )
    ytdl_default_group.add_argument(
        '--no-convert-subs', '--no-convert-sub', '--no-convert-subtitles',
        action='store_const', const=None, dest='convert_subs',
        help='Inverse of --convert-subs.'
    )

    ytdlp_group.add_argument(
        '--no-abort-on-error', action='store_const', const='only_download',
        dest='ignore_errors',
        help=(
            'Continue with next video on download errors; e.g. to skip '
            'unavailable videos in a playlist'
        )
    )
    ytdlp_group.add_argument(
        '--break-on-existing', action='store_true',
        help=(
            'Stop the download process when encountering a file that is in '
            'the archive'
        )
    )
    ytdlp_default_group.add_argument(
        '--no-break-on-existing', action='store_false',
        dest='break_on_existing',
        help='Inverse of --break-on-existing'
    )
    ytdlp_group.add_argument(
        '--break-on-reject', action='store_true',
        help=(
            'Stop the download process when encountering a file that has been '
            'filtered out'
        )
    )
    ytdlp_default_group.add_argument(
        '--no-break-on-reject', action='store_false', dest='break_on_reject',
        help='Inverse of --break-on-reject'
    )
    ytdlp_group.add_argument(
        '--skip-playlist-after-errors', metavar='N', type=_positive_int,
        help=(
            'Number of allowed failures until the rest of the playlist is '
            'skipped'
        )
    )
    ytdlp_group.add_argument(
        '--throttled-rate', metavar='RATE',
        help=(
            'Minimum download rate in bytes per second below which throttling '
            'is assumed and the video data is re-extracted (e.g. 100K)'
        )
    )
    ytdlp_group.add_argument(
        '-P', '--paths', metavar='[TYPES:]PATH', action='append',
        help=(
            'The paths where the files should be downloaded. Specify the type '
            'of file and the path separated by a colon ":". All the same '
            'types as --output are supported. Additionally, you can also '
            'provide "home" (default) and "temp" paths. All intermediary '
            'files are first downloaded to the temp path and then the final '
            'files are moved over to the home path after download is '
            'finished. This option is ignored if --output is an absolute path.'
        )
    )
    ytdlp_group.add_argument(
        '--windows-filenames', action='store_true',
        help='Force filenames to be Windows-compatible'
    )
    ytdlp_default_group.add_argument(
        '--no-windows-filenames', action='store_false',
        dest='windows_filenames',
        help='Inverse of --windows-filenames'
    )
    ytdlp_group.add_argument(
        '--trim-filenames', metavar='LENGTH', type=_positive_int,
        help=(
            'Limit the filename length (excluding extension) to the specified '
            'number of characters'
        )
    )
    ytdlp_default_group.add_argument(
        '--no-force-overwrites', action='store_const', const=None,
        help='Do not overwrite the video, but overwrite related files'
    )
    ytdlp_default_group.add_argument(
        '--write-playlist-metafiles', action='store_true',
        help=(
            'Write playlist metadata in addition to the video metadata when '
            'using --write-info-json, --write-description etc. Inverse of '
            '--no-write-playlist-metafiles.'
        )
    )
    ytdlp_group.add_argument(
        '--no-write-playlist-metafiles', action='store_false',
        dest='write_playlist_metafiles',
        help=(
            'Do not write playlist metadata when using --write-info-json, '
            '--write-description etc.'
        )
    )
    ytdlp_default_group.add_argument(
        '--clean-infojson', action='store_true',
        help=(
            'Remove some private fields such as filenames from the infojson. '
            'Note that it could still contain some personal information. '
            'Inverse of --no-cleaninfojson.'
        )
    )
    ytdlp_group.add_argument(
        '--no-clean-infojson', action='store_false', dest='clean_infojson',
        help='Write all fields to the infojson.'
    )
    ytdlp_group.add_argument(
        '--write-comments', '--get-comments', action='store_true',
        help=(
            'Retrieve video comments to be placed in the infojson. The '
            'comments are fetched even without this option if the extraction '
            'is known to be quick.'
        )
    )
    ytdlp_default_group.add_argument(
        '--no-write-comments', '--no-get-comments', action='store_false',
        dest='write_comments',
        help='Inverse of --write-comments'
    )
    ytdlp_group.add_argument(
        '--write-link', action='store_true',
        help=(
            'Write an internet shortcut file, depending on the current '
            'platform (.url, .webloc or .desktop) of the client. The URL may '
            'be cached by the OS.'
        )
    )
    ytdlp_default_group.add_argument(
        '--no-write-link', action='store_false', dest='write_link',
        help=(
            'Equivalent to passing all of the other --no-write-*-link '
            'args.'
        )
    )
    ytdlp_group.add_argument(
        '--write-url-link', action='store_true',
        help=(
            'Write a .url Windows internet shortcut. The OS caches the URL '
            'based on the file path.'
        )
    )
    ytdlp_default_group.add_argument(
        '--no-write-url-link', action='store_false', dest='write_url_link',
        help='Inverse of --write-url-link.'
    )
    ytdlp_group.add_argument(
        '--write-webloc-link', action='store_true',
        help='Write a .webloc macOS internet shortcut.'
    )
    ytdlp_default_group.add_argument(
        '--no-write-webloc-link', action='store_false',
        dest='write_webloc_link',
        help='Inverse of --write-webloc-link.'
    )
    ytdlp_group.add_argument(
        '--write-desktop-link', action='store_true',
        help='Write a .desktop Linux internet shortcut.'
    )
    ytdlp_default_group.add_argument(
        '--no-write-desktop-link', action='store_false',
        dest='write_desktop_link',
        help='Inverse of --write-desktop-link.'
    )
    ytdlp_group.add_argument(
        '--ignore-no-formats-error', action='store_true',
        help=(
            'Ignore "No video formats" error. Useful for extracting metadata '
            'even if the videos are not actually available for download.'
        )
    )
    ytdlp_default_group.add_argument(
        '--no-ignore-no-formats-error', action='store_false',
        dest='ignore_no_formats_error',
        help='Inverse of --ignore-no-formats-error.'
    )
    ytdlp_group.add_argument(
        '--force-write-archive', '--force-write-download-archive',
        '--force-download-archive', action='store_true',
        help=(
            'Force download archive entries to be written as far as no errors '
            'occur, even if -s or another simulation option is used.'
        )
    )
    ytdlp_default_group.add_argument(
        '--no-force-write-archive', '--no-force-write-download-archive',
        '--no-force-download-archive', action='store_false',
        dest='force_write_archive',
        help='Inverse of --force-write-archive.'
    )
    ytdlp_group.add_argument(
        '--sleep-requests', metavar='SECONDS', type=_positive_float,
        help=(
            'Number of seconds to sleep between requests during data '
            'extraction.'
        )
    )
    ytdlp_group.add_argument(
        '--sleep-subtitles', metavar='SECONDS', type=_positive_int,
        help='Number of seconds to sleep before each subtitle download.'
    )
    ytdlp_group.add_argument(
        '-S', '--format-sort', metavar='SORTORDER', action='append',
        help='Sort the formats by the fields given.'
    )
    ytdlp_group.add_argument(
        '--format-sort-force', '--S-force', action='store_true',
        help=(
            'Force user specified sort order to have precedence over all '
            'fields.'
        )
    )
    ytdlp_default_group.add_argument(
        '--no-format-sort-force', action='store_false',
        dest='format_sort_force',
        help='Inverse of --format-sort-force.'
    )
    ytdlp_group.add_argument(
        '--video-multistreams', action='store_true',
        help='Allow multiple video streams to be merged into a single file.'
    )
    ytdlp_default_group.add_argument(
        '--no-video-multistreams', action='store_false',
        dest='video_multistreams',
        help='Inverse of --video-multistreams.'
    )
    ytdlp_group.add_argument(
        '--audio-multistreams', action='store_true',
        help='Allow multiple audio streams to be merged into a single file.'
    )
    ytdlp_default_group.add_argument(
        '--no-audio-multistreams', action='store_false',
        dest='audio_multistreams',
        help='Inverse of --audio-multistreams.'
    )
    ytdlp_group.add_argument(
        '--check-formats', action='store_const', const='selected',
        help='Check that the selected formats are actually downloadable.'
    )
    ytdlp_group.add_argument(
        '--check-all-formats', action='store_true', dest='check_formats',
        help='Check all formats for whether they are actually downloadable.'
    )
    ytdlp_default_group.add_argument(
        '--no-check-formats', action='store_false', dest='check_formats',
        help=(
            'Do not check that the formats are actually downloadable. Inverse '
            'of --check-formats and --check-all-formats.'
        )
    )
    ytdlp_group.add_argument(
        '--remux-video', metavar='FORMAT',
        help=(
            'Remux the video into another container if necessary. If target '
            'container does not support the video/audio codec, remuxing will '
            'fail. You can specify multiple rules; Eg. "aac>m4a/mov>mp4/mkv" '
            'will remux aac to m4a, mov to mp4 and anything else to mkv.'
        )
    )
    ytdlp_default_group.add_argument(
        '--no-remux-video', action='store_const', const=None,
        dest='remux_video',
        help='Inverse of --remux-video.'
    )
    ytdlp_group.add_argument(
        '--embed-chapters', '--add-chapters', action='store_true',
        help='Add chapter markers to the video file.'
    )
    ytdlp_default_group.add_argument(
        '--no-embed-chapters', '--no-add-chapters', action='store_false',
        dest='embed_chapters',
        help='Inverse of --embed-chapters.'
    )
    ytdlp_group.add_argument(
        '--parse-metadata', metavar='FROM:TO', action='append',
        help='Parse additional metadata like title/artist from other fields.'
    )
    ytdlp_default_group.add_argument(
        '--no-parse-metadata', action='store_const', const=None,
        dest='parse_metadata',
        help='Inverse of --parse-metadata.'
    )
    ytdlp_group.add_argument(
        '--replace-in-metadata', metavar='FIELDS REGEX REPLACE',
        action='append', nargs=3,
        help=(
            'Replace text in a metadata field using the given regex. This '
            'option can be used multiple times.'
        )
    )
    ytdlp_default_group.add_argument(
        '--no-replace-in-metadata', action='store_const', const=None,
        dest='replace_in_metadata',
        help='Inverse of --replace-in-metadata.'
    )
    ytdlp_group.add_argument(
        '--exec-before-download', metavar='CMD', action='append',
        help=(
            'Execute a command before the actual download. The syntax is the '
            'same as --exec but "filepath" is not available. This option can '
            'be used multiple times.'
        )
    )
    ytdlp_group.add_argument(
        '--convert-thumbnails', metavar='FORMAT',
        help='Convert the thumbnails to another format.'
    )
    ytdlp_default_group.add_argument(
        '--no-convert-thumbnails', action='store_const', const=None,
        dest='convert_thumbnails',
        help='Inverse of --convert-thumbnails.'
    )
    ytdlp_group.add_argument(
        '--split-chapters', '--split-tracks', action='store_true',
        help=(
            'Split video into multiple files based on internal chapters. The '
            '"chapter:" prefix can be used with "--paths" and "--output" to '
            'set the output filename for the split files.'
        )
    )
    ytdlp_default_group.add_argument(
        '--no-split-chapters', '--no-split-tracks', action='store_false',
        dest='split_chapters',
        help='Inverse of --split-chapters.'
    )
    ytdlp_group.add_argument(
        '--remove-chapters', metavar='REGEX', action='append',
        help=(
            'Remove chapters whose title matches the given regular '
            'expression. Time ranges prefixed by a "*" can also be used in '
            'place of chapters to remove the specified range. Eg: '
            '--remove-chapters "*10:15-15:00" --remove-chapters "intro". This '
            'option can be used multiple times.'
        )
    )
    ytdlp_default_group.add_argument(
        '--no-remove-chapters', action='store_const', const=None,
        dest='remove_chapters',
        help='Inverse of --remove-chapters.'
    )
    ytdlp_group.add_argument(
        '--force-keyframes-at-cuts', action='store_true', default=False,
        help=(
            'Force keyframes around the chapters before removing/splitting '
            'them. Requires a reencode and thus is very slow, but the '
            'resulting video may have fewer artifacts around the cuts.'
        )
    )
    ytdlp_default_group.add_argument(
        '--no-force-keyframes-at-cuts', action='store_false',
        dest='force_keyframes_at_cuts',
        help='Inverse of --force-keyframes-at-cuts.'
    )
    ytdlp_group.add_argument(
        '--sponsorblock-mark', metavar='CATS', type=_comma_separated_list,
        help=(
            'SponsorBlock categories to create chapters for, separated by '
            'commas. You can prefix the category with a "-" to exempt it.'
        )
    )
    ytdlp_group.add_argument(
        '--sponsorblock-remove', metavar='CATS', type=_comma_separated_list,
        help=(
            'SponsorBlock categories to remove from the video file, separated '
            'by commas. If a category is present in both mark and remove, '
            'remove takes precedence.'
        )
    )
    ytdlp_group.add_argument(
        '--sponsorblock-chapter-title', metavar='TEMPLATE',
        help=(
            'The title template for SponsorBlock chapters created by '
            '--sponsorblock-mark.'
        )
    )
    ytdlp_default_group.add_argument(
        '--no-sponsorblock', action='store_true',
        help='Disable both --sponsorblock-mark and --sponsorblock-remove'
    )
    ytdlp_group.add_argument(
        '--sponsorblock-api', metavar='URL',
        help='SponsorBlock API location.'
    )
    ytdlp_group.add_argument(
        '--extractor-retries', metavar='RETRIES',
        help='Number of retries for known extractor errors, or "infinite".'
    )
    ytdlp_default_group.add_argument(
        '--allow-dynamic-mpd', '--no-ignore-dynamic-mpd', action='store_true',
        help='Process dynamic DASH manifests. Inverse of --ignore-dynamic-mpd.'
    )
    ytdlp_group.add_argument(
        '--ignore-dynamic-mpd', '--no-allow-dynamic-mpd', action='store_false',
        dest='allow_dynamic_mpd',
        help='Do not process dynamic DASH manifests.'
    )
    ytdlp_group.add_argument(
        '--hls-split-discontinuity', action='store_true',
        help=(
            'Split HLS playlists to different formats at discontinuities such '
            'as ad breaks.'
        )
    )
    ytdlp_default_group.add_argument(
        '--no-hls-split-discontinuity', action='store_false',
        dest='hls_split_discontinuity',
        help='Inverse of --hls-split-discontinuity.'
    )
    ytdlp_group.add_argument(
        '--extractor-args', metavar='KEY:ARGS', action='append',
        help=(
            'Pass these arguments to the extractor. You can use this option '
            'multiple times to give arguments for different extractors.'
        )
    )
