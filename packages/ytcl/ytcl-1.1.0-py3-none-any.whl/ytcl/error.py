"""Custom exceptions"""

from __future__ import annotations

__all__ = (
    'YTCLError', 'ArgumentError', 'InvalidArgError',
    'CustomOptNotWhitelistedError', 'HTTPError', 'JobFailedError',
    'JobFinishedError', 'YTDLOptNotWhitelistedError', 'MissingYTDLServerError',
    'UNSPECIFIED_ERROR'
)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any, Optional
    from uuid import UUID

UNSPECIFIED_ERROR = 10
"""Program exit code for unspecified errors"""


class YTCLError(Exception):
    """Base exception for this module"""

    __slots__ = ()

    EXIT_CODE = UNSPECIFIED_ERROR
    """Program exit code

    This should be overridden by subclasses so that each exception has a
    unique exit code.
    """


class ArgumentError(YTCLError):
    """Base exception for argparse argument errors"""

    __slots__ = ()

    EXIT_CODE = 2
    """Program exit code

    This is the same code that `argparse.ArgumentParser.error()` raises.
    """


class InvalidArgError(ArgumentError):
    """Raised by some subclasses of `base.Base.from_argparse()` when an
    arg has an invalid value"""

    __slots__ = ('arg', 'msg')

    arg: str
    """Name of the argument"""
    msg: str
    """Message describing the error"""

    def __init__(self, arg: str, msg: str) -> None:
        self.arg = arg
        self.msg = msg

    def __str__(self) -> str:
        return f'{self.arg}: {self.msg}'


class YTDLOptNotWhitelistedError(YTCLError):
    """Raised by `opts.YTDLOpt.get_pair()` and
    `create.Create.from_argparse()` when the user attempts to use a
    ytdl_opt that isn't whitelisted"""

    __slots__ = ('ytdl_opt', 'msg')

    EXIT_CODE = 11

    ytdl_opt: str
    """Name of the ytdl_opt that caused the error"""
    msg: str
    """Message describing the error"""

    def __init__(self, ytdl_opt: str, msg: Optional[str] = None) -> None:
        self.ytdl_opt = ytdl_opt
        if msg is not None:
            self.msg = msg
        else:
            self.msg = (
                f'ytdl_opt isn\'t whitelisted: {ytdl_opt}. '
                'Check the ytdl-server documentation'
            )

    def __str__(self) -> str:
        return self.msg


class CustomOptNotWhitelistedError(YTCLError):
    """Raised by `opts.CustomOpt.get_pair()` and
    `create.Create.from_argparse()` when the user attempts to use a
    custom_opt that isn't whitelisted"""

    __slots__ = ('custom_opt', 'msg')

    EXIT_CODE = 12

    custom_opt: str
    """Name of the custom_opt that caused the error"""
    msg: str
    """Message describing the error"""

    def __init__(self, custom_opt: str, msg: Optional[str] = None) -> None:
        self.custom_opt = custom_opt
        if msg is not None:
            self.msg = msg
        else:
            self.msg = (
                f'custom_opt isn\'t whitelisted: {custom_opt}. '
                'Check the ytdl-server documentation'
            )

    def __str__(self) -> str:
        return self.msg


class JobFinishedError(YTCLError):
    """Raised by `cancel.Cancel.start()` when a job finishes before it
    could be cancelled"""

    __slots__ = ('job_id', 'status', 'msg')

    EXIT_CODE = 13

    job_id: UUID
    """Job ID"""
    status: str
    """Job status"""
    msg: str
    """Message describing the error"""

    def __init__(
        self, job_id: UUID, status: str, msg: Optional[str] = None
    ) -> None:
        self.job_id = job_id
        self.status = status
        if msg is not None:
            self.msg = msg
        else:
            self.msg = (
                'The job finished before it could be cancelled. '
                f'Status: {status}'
            )

    def __str__(self) -> str:
        return self.msg


class JobFailedError(YTCLError):
    """Raised by `base.Base.start()` when a job fails"""

    __slots__ = ('job_id', 'status', 'msg')

    EXIT_CODE = 14

    job_id: UUID
    """Job ID"""
    status: str
    """Job status"""
    msg: str
    """Message describing the error"""

    def __init__(
        self, job_id: UUID, status: str, msg: Optional[str] = None
    ) -> None:
        self.job_id = job_id
        self.status = status
        if msg is not None:
            self.msg = msg
        else:
            self.msg = f'Job failed with status {status!r}: {job_id}'

    def __str__(self) -> str:
        return self.msg


class HTTPError(YTCLError):
    """Raised by functions in `http` when the ytdl-server returns an
    error response"""

    __slots__ = ('code', 'response', 'msg')

    EXIT_CODE = 15

    _BLACKLISTED_KEYS = frozenset((
        'code', 'description', 'error', 'status_url'
    ))
    """Set of keys within the response that won't be added to the error
    message"""

    code: int
    """HTTP status code"""
    response: dict[str, Any]
    """JSON response data"""
    msg: str
    """Message describing the error"""

    def __init__(
        self, code: int, response: Mapping[str, Any], msg: Optional[str] = None
    ) -> None:
        self.code = code
        self.response = dict(response)

        if msg is not None:
            self.msg = msg
        else:
            if 'description' in self.response:
                description = self.response['description']
            elif 'error' in self.response:
                description = self.response['error']
            else:
                description = 'Unrecognized error'

            msg_list = [
                f'ytdl-server error: {description}.'
            ]

            extra_fields = tuple(
                f'{key.capitalize()}: {value}'
                for key, value in sorted(self.response.items())
                if key not in self._BLACKLISTED_KEYS
            )
            if extra_fields:
                msg_list.append(', '.join(extra_fields))

            self.msg = '\n'.join(msg_list)

    def __str__(self) -> str:
        return self.msg


class MissingYTDLServerError(YTCLError):
    """Raised by `base.Base()` when the `server` attribute isn't given"""

    __slots__ = ('msg',)

    EXIT_CODE = 16

    msg: str
    """Message describing the error"""

    def __init__(self, msg: Optional[str] = None) -> None:
        if msg is not None:
            self.msg = msg
        else:
            self.msg = (
                'The ytdl-server URL wasn\'t given. You must provide it via '
                'the --ytdl-server arg or via the $YTDL_SERVER env-var.'
            )

    def __str__(self) -> str:
        return self.msg
