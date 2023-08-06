"""Parse the ytdl-server config"""

from __future__ import annotations

__all__ = ('YTDLConfig', 'DEFAULT',)

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse
    from collections.abc import Mapping
    from typing import Any, Optional

    from . import http

DEFAULT = object()
"""Default sentinel value used by `YTDLConfig`"""


@dataclass(frozen=True)
class YTDLConfig:
    """Dataclass that represents the ytdl-server config as returned by
    '//YTDL_SERVER/config'

    Unused fields are omitted
    """
    ytdl_default_opts: dict[str, Any]
    ytdl_whitelist: Optional[frozenset[str]]
    custom_default_opts: dict[str, Any]
    custom_whitelist: Optional[frozenset[str]]

    @classmethod
    def from_dict(cls, dict_: Mapping[str, Any]) -> YTDLConfig:
        """Construct an instance from the given mapping"""
        kwargs = {
            'ytdl_default_opts': dict_['ytdl_default_opts'],
            'ytdl_whitelist': dict_['ytdl_whitelist'],
            'custom_default_opts': dict_['custom_default_opts'],
            'custom_whitelist': dict_['custom_whitelist']
        }
        for key in ('ytdl_whitelist', 'custom_whitelist'):
            # Convert the whitelists to sets when they're not `None`
            if kwargs[key] is not None:
                kwargs[key] = frozenset(kwargs[key])

        return cls(**kwargs)

    @classmethod
    def from_opener(cls, opener: http.Opener) -> YTDLConfig:
        """Construct an instance by using the given `http.Opener`
        instance to query the ytdl-server
        """
        _, data = opener.get('config')
        return cls.from_dict(data)

    def ytdl_opt_from_args(
        self, args: argparse.Namespace, ytdl_opt: str,
        arg: Optional[str] = None, default: Any = DEFAULT
    ) -> Any:
        """Return the value of the given ytdl_opt

        First checks the argparse namespace. If the value isn't found
        there, the ytdl default opts will be checked

        Raises `KeyError` if no value is found when `default` isn't
        given

        args: The argparse namespace that will be checked
        ytdl_opt: Name of the ytdl_opt within `self.ytdl_default_opts`
        arg: Name of the argument within `args`. Defaults to the same
            value as `ytdl_opt`
        default: This value will be used as a fallback if the ytdl_opt
            isn't found
        """
        if arg is None:
            arg = ytdl_opt

        if arg in args:
            return getattr(args, arg)
        elif ytdl_opt in self.ytdl_default_opts:
            return self.ytdl_default_opts[ytdl_opt]
        elif default is not DEFAULT:
            return default
        else:
            raise KeyError(ytdl_opt)

    def custom_opt_from_args(
        self, args: argparse.Namespace, custom_opt: str,
        arg: Optional[str] = None, default: Any = DEFAULT
    ) -> Any:
        """Return the value of the given custom_opt

        First checks the argparse namespace. If the value isn't found
        there, the custom default opts will be checked

        Raises `KeyError` if no value is found when `default` isn't
        given

        args: The argparse namespace that will be checked
        custom_opt: Name of the custom_opt within
            `self.custom_default_opts`
        arg: Name of the argument within `args`. Defaults to the same
            value as `custom_opt`
        default: This value will be used as a fallback if the custom_opt
            isn't found
        """
        if arg is None:
            arg = custom_opt

        if arg in args:
            return getattr(args, arg)
        elif custom_opt in self.custom_default_opts:
            return self.custom_default_opts[custom_opt]
        elif default is not DEFAULT:
            return default
        else:
            raise KeyError(custom_opt)

    def is_ytdl_whitelisted(self, ytdl_opt: str) -> bool:
        """Returns `True` if the given ytdl_opt is whitelisted

        Also returns `True` if the whitelist is disabled
        """
        if self.ytdl_whitelist is None:
            return True
        return ytdl_opt in self.ytdl_whitelist

    def is_custom_whitelisted(self, custom_opt: str) -> bool:
        """Returns `True` if the given custom_opt is whitelisted

        Also returns `True` if the whitelist is disabled
        """
        if self.custom_whitelist is None:
            return True
        return custom_opt in self.custom_whitelist
