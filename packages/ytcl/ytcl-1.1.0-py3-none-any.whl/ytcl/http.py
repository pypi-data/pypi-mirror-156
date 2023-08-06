"""Communicate with the ytdl-server REST API"""

from __future__ import annotations

__all__ = ('Opener', 'urljoin')

import json
import logging
import os
import urllib.error
import urllib.request
from collections.abc import Mapping
from typing import TYPE_CHECKING

from . import error as ytcl_error
from .util import prompt_pass

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any, Optional


class Opener:
    """Helper class for communicating with the ytdl-server REST API

    Example:
        opener = Opener('http://ytdl.example.com')

        # Set up basic auth. Optional
        opener.add_auth('USER', 'PASSWD')

        # POST
        opener.post('jobs/', data=...)
        # GET
        opener.get('jobs/{job_id}')

    You can also use `from_env()` to construct an instance via env-vars.
    """

    __slots__ = (
        'root_url', '_password_mgr', '_handler', '_opener'
    )

    root_url: str
    """Root URL of the ytdl-server API"""

    def __init__(self, root_url: str) -> None:
        self.root_url = root_url

        self._password_mgr = urllib.request.HTTPPasswordMgrWithPriorAuth()
        self._handler = urllib.request.HTTPBasicAuthHandler(self._password_mgr)
        self._opener = urllib.request.build_opener(self._handler)

    def add_auth(self, user: str, password: str) -> None:
        """Set up basic authentication"""
        self._password_mgr.add_password(
            realm=None, uri=self.root_url, user=user, passwd=password
        )

    def get(
        self, path: Optional[str] = None, log: bool = True
    ) -> tuple[int, dict[str, Any]]:
        """GET the given path

        Path is appended to `root_url` if given.

        If `log` is `True`, debug messages will be logged.

        Returns the status code and the JSON response data.

        Raises an exception if the response has a 400-599 status code,
        or if the response data isn't valid JSON.
        """
        return self._open('GET', path, None, log)

    def post(
        self, path: Optional[str] = None, data: Any = None, log: bool = True
    ) -> tuple[int, dict[str, Any]]:
        """POST to the given path

        `data` is an optional JSONable object that will be used as the
        request data if given.

        Other behavior is identical to `get()`.
        """
        return self._open('POST', path, data, log)

    def patch(
        self, path: Optional[str] = None, data: Any = None, log: bool = True
    ) -> tuple[int, dict[str, Any]]:
        """PATCH the given path

        Behavior is identical to `post()`.
        """
        return self._open('PATCH', path, data, log)

    def _open(
        self, method: str, path: Optional[str], data: Any, log: bool
    ) -> tuple[int, dict[str, Any]]:
        if path is not None:
            url = urljoin(self.root_url, path)
        else:
            url = self.root_url

        if log:
            logging.debug(
                'HTTP request: Method=%s | URL=%r | Data=%r', method, url, data
            )

        if data is not None:
            json_data: Optional[bytes] = json.dumps(data).encode('utf-8')
        else:
            json_data = None

        request = urllib.request.Request(url, data=json_data, method=method)
        if data is not None:
            request.add_header('Content-Type', 'application/json')

        try:
            with self._opener.open(request) as response:
                code = response.status
                response_data = json.load(response)
        except urllib.error.HTTPError as e:
            # Attempt to load the JSON response data, and abort if it's
            # not JSON
            try:
                error_json = json.load(e)
            except json.JSONDecodeError:
                error_json = None

            if isinstance(error_json, Mapping):
                # Convert the exception to a custom ytcl exception so
                # that we can pretty-print the JSON response object
                raise ytcl_error.HTTPError(e.code, error_json) from e
            else:
                # Re-raise the original exception if the response isn't
                # a JSON object
                raise

        if log:
            logging.debug('HTTP response: Code=%s', code)

        return code, response_data

    @classmethod
    def from_env(
        cls, root_url: Optional[str] = None, user: Optional[str] = None,
        password: Optional[str] = None
    ) -> Opener:
        """Construct an instance from the relevant env-vars

        If any of the arguments are given they will be used instead of
        checking the env-var.

        If `root_url` isn't given and its env-var isn't set,
        `MissingYTDLServerError` will be raised.

        If `user` is given but `password` isn't, the user will be
        prompted for the password.
        """
        if root_url is None:
            try:
                root_url = cls._get_env_var(
                    'YTDL_SERVER', deprecated_aliases=('YTCL_SERVER',)
                )
            except ValueError as e:
                raise ytcl_error.MissingYTDLServerError() from e

        if user is None:
            try:
                user = cls._get_env_var(
                    'YTDL_SERVER_USERNAME',
                    deprecated_aliases=('YTCL_SERVER_USERNAME',)
                )
            except ValueError:
                pass

        if password is None:
            try:
                password = cls._get_env_var(
                    'YTDL_SERVER_PASSWORD', censor_log=True,
                    deprecated_aliases=('YTCL_SERVER_PASSWORD',)
                )
            except ValueError:
                prompt_for_pass = user is not None
            else:
                prompt_for_pass = False

            if prompt_for_pass:
                password = prompt_pass('ytdl-server password: ')

        opener = cls(root_url)
        if user is not None:
            # Ignore type warning about `password` being `None`.
            # `password` is always a str when `user` is a str.
            opener.add_auth(user, password)  # type: ignore[arg-type]

        return opener

    @staticmethod
    def _get_individual_env_var(
        env_var: str, censor_log: bool, preferred_env_var: Optional[str] = None
    ) -> Optional[str]:
        """Get a single env-var, and return its value if defined

        Used by `_get_env_var()`.

        If `preferred_env_var` isn't `None`, a deprecation warning will
        be logged if the env-var is defined.
        """
        value = os.environ.get(env_var)
        if value:
            value = os.environ[env_var]
            display_value = '***' if censor_log else value
            logging.debug('Loaded env-var: $%s=%r', env_var, display_value)

            if preferred_env_var is not None:
                logging.warning(
                    'The env-var $%s is deprecated. Use $%s instead.',
                    env_var, preferred_env_var
                )

            return value

        return None

    @classmethod
    def _get_env_var(
        cls, env_var: str, censor_log: bool = False,
        deprecated_aliases: Optional[Iterable[str]] = None
    ) -> str:
        """Load the given env-var and return the value

        Raises `ValueError` if the env-var isn't defined or if it's
        an empty string.

        If `censor_log` is `True`, the value of the env-var won't be
        logged.

        `deprecated_aliases` is an optional list of alternative env-vars
        that have been deprecated. If the main env-var isn't defined,
        these aliases will also be checked. The first matching env-var
        (if any) will be used, and a deprecation warning will be logged.
        """
        value = cls._get_individual_env_var(env_var, censor_log)
        if value is not None:
            return value

        if deprecated_aliases is not None:
            for alias in deprecated_aliases:
                value = cls._get_individual_env_var(
                    alias, censor_log, preferred_env_var=env_var
                )
                if value is not None:
                    return value

        raise ValueError(f'Env-var is unset: {env_var}')


def urljoin(*components: str) -> str:
    """Combine the given components into a URL

    A single slash is added between each component if needed.
    """
    last_index = len(components) - 1
    url: list[str] = []

    for i, component in enumerate(components):
        if i > 0 and component.startswith('/'):
            # Remove leading slash
            component = component[1:]
        if i < last_index and component.endswith('/'):
            # Remove trailing slash
            component = component[:-1]
        url.append(component)

    return '/'.join(url)
