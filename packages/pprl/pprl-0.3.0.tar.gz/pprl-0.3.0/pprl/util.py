"""
This module contains utility functions and classes used internally by the PPRL package.
"""

from typing import Dict

import requests

from .model import ApiError


def _append_path(base_url: str, path: str) -> str:
    if base_url[-1] != '/':
        base_url += '/'

    return base_url + path


def _check_response_errors(
        r: requests.Response,
        expected_code: int,
        error_mapping: Dict[int, str]
):
    c = r.status_code

    if c != expected_code:
        print(r.text)
        raise ApiError(error_mapping.get(c, "Couldn't fetch resource"), c)


class GenericRestClient:
    """
    Generic class which holds a base URL under which a REST service is accessible.
    """

    def __init__(self, base_url: str):
        """
        Creates a new generic REST client.

        :param base_url: Base URL at which the REST API service is hosted
        """
        self._base_url = base_url
