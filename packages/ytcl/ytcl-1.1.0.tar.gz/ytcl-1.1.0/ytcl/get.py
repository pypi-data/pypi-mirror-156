"""Subparser for getting the status of a job"""

from __future__ import annotations

__all__ = ('Get',)

import json
import time
from typing import TYPE_CHECKING

from . import ansi, http
from .base import Base, FormatEnum, ProgressEnum
from .error import JobFailedError
from .util import format_timestamp

if TYPE_CHECKING:
    import argparse
    from typing import Any, Optional
    from uuid import UUID


class Get(Base):
    """Subparser class that's used to get the status of a job and print
    the output"""

    __slots__ = ('job_id', 'log_lines', 'get_path', '_response_data')

    job_id: UUID
    """Job ID to get the status of"""
    log_lines: int
    """Number of log lines to initially print when `output_format` is
    `progress`

    If the value is `0`, all logs will be printed.
    """
    get_path: str
    """URL path used to get the job status"""

    _response_data: dict[str, Any]

    def __init__(self, *, job_id: UUID, log_lines: int, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.job_id = job_id
        self.log_lines = log_lines

        self.get_path = http.urljoin('jobs', str(job_id))

    @classmethod
    def _get_kwargs(cls, args: argparse.Namespace) -> dict[str, Any]:
        kwargs = super()._get_kwargs(args)
        kwargs.update({
            'job_id': args.job_id,
            'log_lines': args.log_lines
        })
        return kwargs

    def start(self) -> None:
        """Get the status of a job and print the output"""
        first_log = -self.log_lines

        if self.output_format is FormatEnum.JSON:
            self._get_status()
            self.print(json.dumps(self._response_data))
        elif self.output_format is FormatEnum.ALL:
            self._get_status()
            self._print_all()
        else:  # self.output_format is FormatEnum.PROGRESS
            if self.detach:
                self._get_status()
                self._print_progress(first_log)
            else:
                self._progress_loop(first_log)

    def _get_status(self, log: bool = True) -> None:
        """Get the current job status and set `_response_data`

        If `log` is `True`, debug messages will be logged.
        """
        _, self._response_data = self.opener.get(self.get_path, log)

    def _format_header(self, text: Any) -> str:
        """Colorize the given value for use as a header when
        --output-format=all

        Also adds a trailing colon.
        """
        return f'{self.format_bold(text)}:'

    def _format_status(self, status: str) -> str:
        """Colorize the given job status"""
        if not self.use_escape_codes:
            return status

        if status == 'finished':
            color: Optional[ansi.FGColor] = ansi.FGColor.GREEN
        elif status == 'cancelled':
            color = ansi.FGColor.YELLOW
        elif status in self.ERROR_STATUSES:
            color = ansi.FGColor.RED
        else:
            color = None

        if color is not None:
            return ansi.format_fg_color(status, color)
        else:
            return status

    def _print_all(self) -> None:
        """Print the entire job status for when --output-format=all"""
        self.print(
            self._format_header('Status'),
            self._format_status(self._response_data['status'])
        )

        if self._response_data['error'] is not None:
            self.print(
                self._format_header('Error'), self._response_data['error']
            )

        if self._response_data['started'] is not None:
            self.print(
                self._format_header('Time started'),
                format_timestamp(self._response_data['started'])
            )
        if self._response_data['finished'] is not None:
            self.print(
                self._format_header('Time finished'),
                format_timestamp(self._response_data['finished'])
            )

        formatted_urls = ', '.join(
            repr(url) for url in self._response_data['urls']
        )
        self.print(self._format_header('Video URLs'), formatted_urls)

        if self._response_data['ytdl_opts'] is not None:
            self.print(self._format_header('YTDL Options'), '{')
            for key, value in self._response_data['ytdl_opts'].items():
                self.print(f'  {key}: {value!r}')
            self.print('}')

        if self._response_data['logs']:
            self.print(self._format_header('Logs'), '[')
            for log in self._response_data['logs']:
                self.print(f'  {self.format_log(log)}')
            self.print(']')

        if self._response_data['progress']:
            self.print(self._format_header('Progress'), '[')
            for progress in self._response_data['progress']:
                self.print(
                    f'  {self.format_progress(progress, real_time=False)}'
                )
            self.print(']')

    def _print_progress(
        self, first_log: int, end_new_line: bool = True,
        overwrite_line: bool = False, prev_progress_len: int = 0
    ) -> int:
        """Print the job status for when --output-format=progress

        Only log entries with an index >= `first_log` will be printed.
        You can set this to the length of the log array on the previous
        run in order to only print new entries.

        You can also set `first_log` to a negative number in order to
        only print the newest *n* entries.

        If `end_new_line` is `True`, a new line will be printed after
        printing the progress.
        This should be set to `False` if you plan on
        using `overwrite_line`.

        If `overwrite_line` is `True`, the current line will be
        overwritten. You can use this to avoid printing multiple
        progress lines.
        This has no effect if `self.progress_mode` is not `OVERWRITE`.

        If `self.use_escape_codes` is `False`, the previous progress
        will be overwritten by padding it with trailing whitespace
        instead of using ANSI escape codes.
        `prev_progress_len` is used to determine the amount of
        whitespace needed.

        Returns the length of the download progress line. You can use
        this as the value to `prev_progress_len`.
        """
        if end_new_line:
            progress_end = '\n'
        else:
            progress_end = ''

        if overwrite_line and self.progress_mode is ProgressEnum.OVERWRITE:
            if self.use_escape_codes:
                # Using ANSI escape codes is preferred because it avoids
                # unexpected line wrapping that's caused by padding with
                # whitespace.
                self.print(ansi.reset_line(), end='')
            else:
                # Overwrite the current line via whitespace
                padding = ' ' * prev_progress_len
                self.print(f'\r{padding}\r', end='')

        if self._response_data['logs']:
            for log in self._response_data['logs'][first_log:]:
                self.print(self.format_log(log))

        if (
            self._response_data['progress'] and
            self.progress_mode is not ProgressEnum.NONE
        ):
            progress = self.format_progress(
                self._response_data['progress'][-1]
            )
            progress_len = len(progress)
            # For some reason, this carriage return is needed in order
            # for the progress to be visible on Windows when whitespace
            # is used to overwrite the last line.
            self.print(f'\r{progress}', end=progress_end)
        else:
            # Length doesn't matter when the progress isn't printed.
            progress_len = 0

        return progress_len

    def _progress_loop(self, first_log: int) -> None:
        """Print progress in a loop until the job finishes"""
        first_loop = True
        end_new_line = self.progress_mode is not ProgressEnum.OVERWRITE
        prev_progress_len = 0

        while True:
            self._get_status(log=first_loop)
            prev_progress_len = self._print_progress(
                first_log=first_log, end_new_line=end_new_line,
                overwrite_line=not first_loop,
                prev_progress_len=prev_progress_len
            )

            if self._response_data['status'] not in self.IN_PROGRESS_STATUSES:
                break

            first_log = len(self._response_data['logs'])
            first_loop = False
            time.sleep(self.interval)

        # Ensure that the output ends with a new line
        if self.progress_mode is ProgressEnum.OVERWRITE and prev_progress_len:
            self.print()

        status = self._response_data['status']
        if status in self.ERROR_STATUSES:
            error_msg = self._generate_job_failed_message(
                status, self._response_data['error']
            )
            raise JobFailedError(self.job_id, status, error_msg)
        else:
            formatted_job_id = self.format_bold(self.job_id)
            if status == 'cancelled':
                self.print('Job cancelled:', formatted_job_id)
            else:
                self.print('Job finished:', formatted_job_id)

    def _generate_job_failed_message(
        self, status: str, error: Optional[str]
    ) -> str:
        """Generate a custom-formatted message for `JobFailedError`
        exceptions

        status: Job status.
        error: The 'error' field from the response data. This will be
            appended to the message if it exists.
        """
        formatted_job_id = self.format_bold(self.job_id)

        if status == 'error':
            msg = f'Job failed: {formatted_job_id}'
        elif status == 'timeout':
            msg = f'Job timed out: {formatted_job_id}'
        else:
            msg = f'Job failed with status {status!r}: {formatted_job_id}'

        if error:
            msg += f'\n{error}'

        return msg
