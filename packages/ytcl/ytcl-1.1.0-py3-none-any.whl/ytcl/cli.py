"""Run ytcl as a command-line interface"""

from __future__ import annotations

__all__ = ('main',)

import locale
import logging
import os.path
import signal
import sys
from typing import TYPE_CHECKING

# Optional dependency. Used to convert ANSI escape codes on Windows.
try:
    import colorama
except ImportError:
    colorama = None  # type: ignore[assignment]

from .args import get_parser
from .cancel import Cancel
from .create import Create
from .error import ArgumentError, JobFailedError, UNSPECIFIED_ERROR, YTCLError
from .get import Get

if TYPE_CHECKING:
    import argparse
    from types import FrameType
    from typing import Optional

    from .base import Base

_SUBCOMMANDS = {
    'get': Get,
    'create': Create,
    'cancel': Cancel
}
"""Mapping of subparsers to their corresponding classes"""


def _signal_handler(signum: int, frame: Optional[FrameType]) -> None:
    """Catch signals, and warn the user that the job is still running
    in the background before exiting"""
    signame = signal.Signals(signum).name
    logging.info('Caught signal: %s. Terminating', signame)

    prog = os.path.basename(sys.argv[0])
    logging.warning(
        'If you created a job, it\'s still running on the server. '
        'To cancel it, run `%s cancel $JOB_ID`', prog
    )

    # Exit with the signal-specific exit code on Linux.
    # https://tldp.org/LDP/abs/html/exitcodes.html
    sys.exit(128 + signum)


def _set_signal_handlers() -> None:
    """Set up the signal handler for SIGINT and SIGTERM"""
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, _signal_handler)


def _configure_logging(level: int) -> None:
    """Configure logging to stderr"""
    logging.basicConfig(level=level, format='[%(levelname)s] %(message)s')


def _run_subparser(args: argparse.Namespace) -> None:
    # Mypy incorrectly thinks that the type of `Subparser` is `ABCMeta`
    Subparser: type[Base] = (
        _SUBCOMMANDS[args.subparser]  # type: ignore[assignment]
    )
    subparser = Subparser.from_argparse(args)
    _set_signal_handlers()
    subparser.start()


def _init_colorama() -> bool:
    """Initialize Colorama if it's installed

    Colorama is required for ANSI escape codes to work on Windows.

    Returns `True` if Colorama was initialized.
    """
    if colorama:
        logging.debug('Colorama is installed. Initializing')
        colorama.init()
        return True
    else:
        logging.debug('Colorama isn\'t installed. Skipping initializaton')
        return False


def main() -> None:
    """Parse arguments, set up logging, and run the needed subparser
    function"""
    parser = get_parser()
    args = parser.parse_args()

    # Use the user's locale settings for timestamps
    locale.setlocale(locale.LC_TIME, '')

    if args.quiet:
        log_level = logging.ERROR
    elif args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    _configure_logging(log_level)

    logging.debug('Args: %s', args)

    # Initialize Colorama, and disable ANSI escape codes if it's not
    # installed when using Windows.
    colorama_enabled = _init_colorama()
    if not colorama_enabled and sys.platform == 'win32':
        if args.color == 'auto':
            logging.warning(
                'Color output disabled because Colorama is not installed. '
                'You can disable this warning by passing --color=never'
            )
            args.color = 'never'

    try:
        _run_subparser(args)
    except ArgumentError as e:
        parser.error(str(e))
    except JobFailedError as e:
        # Log to stdout instead of stderr
        print(e)
        sys.exit(e.EXIT_CODE)
    except YTCLError as e:
        logging.critical(e)
        sys.exit(e.EXIT_CODE)
    except Exception as e:
        # Unexpected exception. Only log the full traceback when
        # --verbose is given.
        if args.verbose:
            logging.critical(e, exc_info=e)
        else:
            logging.critical(e)
        sys.exit(UNSPECIFIED_ERROR)
