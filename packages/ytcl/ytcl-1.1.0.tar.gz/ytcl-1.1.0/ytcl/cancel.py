"""Subparser for cancelling jobs"""

from __future__ import annotations

__all__ = ('Cancel',)

import logging
import os.path
import sys
import time
from typing import TYPE_CHECKING

from . import http
from .base import Base
from .error import JobFinishedError

if TYPE_CHECKING:
    import argparse
    from typing import Any
    from uuid import UUID


class Cancel(Base):
    __slots__ = ('job_id', 'url_path')

    job_id: UUID
    """Job ID to cancel"""

    url_path: str
    """URL path used to cancel the job as well as get the status"""

    def __init__(self, *, job_id: UUID, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.job_id = job_id
        self.url_path = http.urljoin('jobs', str(job_id))

    @classmethod
    def _get_kwargs(cls, args: argparse.Namespace) -> dict[str, Any]:
        kwargs = super()._get_kwargs(args)
        kwargs.update({
            'job_id': args.job_id
        })
        return kwargs

    def start(self) -> None:
        code, response_data = self.opener.patch(self.url_path, {
            'status': 'cancelled'
        })

        if code == 200:
            logging.info('Job has already been cancelled')
        elif code == 202:
            if self.detach:
                prog = os.path.basename(sys.argv[0])
                logging.info(
                    'Cancel request sent. To check the status of the job, '
                    'run `%s get %s`',
                    prog, self.job_id
                )
            else:
                logging.info(
                    'Cancel request sent. Waiting for job to be cancelled',
                )
                self._wait_loop()

    def _wait_loop(self) -> None:
        """Wait for the job to be cancelled"""
        while True:
            time.sleep(self.interval)

            _, response_data = self.opener.get(self.url_path)
            status = response_data['status']

            if status == 'cancelled':
                logging.info('Job successfully cancelled')
                break
            elif status not in self.IN_PROGRESS_STATUSES:
                raise JobFinishedError(self.job_id, status)
