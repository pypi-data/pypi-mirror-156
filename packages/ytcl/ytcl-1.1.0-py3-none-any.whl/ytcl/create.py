"""Subparser for creating jobs"""

from __future__ import annotations

__all__ = ('Create',)

import logging
from typing import TYPE_CHECKING
from uuid import UUID

from .base import Base, FormatEnum
from .config import YTDLConfig
from .error import InvalidArgError
from .get import Get
from .opts import create_custom_opts, create_ytdl_opts

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping
    from typing import Any, Optional, TextIO

    import argparse


class Create(Base):
    __slots__ = (
        'urls', 'ytdl_opts', 'custom_opts', '_base_kwargs'
    )

    urls: tuple[str, ...]
    """List of video URLs to download"""
    ytdl_opts: Optional[dict[str, Any]]
    """ytdl_opts to use when creating the job"""
    custom_opts: Optional[dict[str, Any]]
    """custom_opts to use when creating the job"""

    POST_PATH = 'jobs/'
    """URL path used to create (POST) the job"""

    _base_kwargs: dict[str, Any]
    """Base __init__() kwargs that will be passed to `Get()` when
    created"""

    def __init__(
        self, *, urls: Iterable[str], ytdl_opts: Optional[Mapping[str, Any]],
        custom_opts: Optional[Mapping[str, Any]], **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.urls = tuple(urls)
        self._base_kwargs = kwargs

        if ytdl_opts is not None:
            self.ytdl_opts = dict(ytdl_opts)
        else:
            self.ytdl_opts = None

        if custom_opts is not None:
            self.custom_opts = dict(custom_opts)
        else:
            self.custom_opts = None

    @classmethod
    def _get_kwargs(cls, args: argparse.Namespace) -> dict[str, Any]:
        kwargs = super()._get_kwargs(args)

        urls: list[str] = []
        if 'batch_file' in args:
            urls += cls._read_batch_file(args.batch_file)
            args.batch_file.close()
        urls += args.url

        if not urls:
            raise InvalidArgError(
                'url',
                'you must provide at least one URL, '
                'either directly or via --batch-file'
            )

        logging.debug('Getting ytdl-server config')
        config = YTDLConfig.from_opener(kwargs['opener'])

        ytdl_opts = create_ytdl_opts(args, config)
        custom_opts = create_custom_opts(args, config)

        kwargs.update({
            'urls': urls,
            'ytdl_opts': ytdl_opts,
            'custom_opts': custom_opts
        })
        return kwargs

    def start(self) -> None:
        """Create the job and print the output using `get.Get`"""
        request_data: dict[str, Any] = {
            'urls': self.urls
        }
        if self.ytdl_opts is not None:
            request_data['ytdl_opts'] = self.ytdl_opts
        if self.custom_opts is not None:
            request_data['custom_opts'] = self.custom_opts

        _, response_data = self.opener.post(self.POST_PATH, request_data)
        job_id = response_data['id']

        if self.output_format is not FormatEnum.JSON:
            self.print('Job ID:', self.format_bold(job_id))

        # Get the job status. All log lines will be printed.
        get = Get(job_id=UUID(job_id), log_lines=0, **self._base_kwargs)
        get.start()

    @staticmethod
    def _read_batch_file(file: TextIO) -> tuple[str, ...]:
        """Get a list of URLs from the file

        Used by the --batch-file arg

        Lines starting with '#', ';', or ']' are ignored
        """
        logging.debug('Reading batch file: %s', file.name)
        urls = []

        for line in file:
            url = line.strip()
            if url and not url.startswith(('#', ';', ']')):
                urls.append(url)

        logging.info('URLs from batch file: %s', urls)
        return tuple(urls)
