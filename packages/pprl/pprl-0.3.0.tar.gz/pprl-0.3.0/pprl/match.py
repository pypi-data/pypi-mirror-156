"""
This module contains functions for interacting with the PPRL match service
provided by the Medical Data Science Group Leipzig.
"""

from typing import List

import requests

from .model import ApiError, MatchConfiguration, MatchResult
from .schema import _serialize_match_configuration, _deserialize_match_result
from .util import _append_path, _check_response_errors, GenericRestClient


def get_match_methods(base_url: str) -> List[str]:
    """
    Returns a list of match methods supported by the matcher.

    :param base_url: Match service base URL
    :return: List of supported match methods
    """
    url = _append_path(base_url, "match-methods")
    r = requests.get(url)

    if r.status_code != requests.codes.ok:
        raise ApiError("Couldn't fetch match methods", r.status_code)

    return r.json()


def get_match_modes(base_url: str) -> List[str]:
    """
    Returns a list of match modes supported by the matcher.

    :param base_url: Match service base URL
    :return: List of supported match modes
    """
    url = _append_path(base_url, "match-modes")
    r = requests.get(url)

    if r.status_code != requests.codes.ok:
        raise ApiError("Couldn't fetch match modes", r.status_code)

    return r.json()


def match(
        base_url: str,
        config: MatchConfiguration,
        domain_list: List[str],
        range_list: List[str]
) -> List[MatchResult]:
    """
    Computes the similarity between a list of domain and range bit vectors using the
    provided match configuration.

    :param base_url: Match service base URL
    :param config: Match configuration
    :param domain_list: List of domain bit vectors
    :param range_list: List of range bit vectors
    :return: Computed similarities according to match configuration
    """
    if len(domain_list) == 0 or len(range_list) == 0:
        return []

    url = _append_path(base_url, "match")
    r = requests.post(url, json={
        "config": _serialize_match_configuration(config),
        "domain": domain_list,
        "range": range_list
    })

    _check_response_errors(r, requests.codes.ok, {
        requests.codes.bad_request: "Invalid match configuration"
    })

    return [
        _deserialize_match_result(c) for c in r.json()["correspondences"]
    ]


class MatchClient(GenericRestClient):
    """
    Wrapper around the API endpoints exposed by the match service.
    """

    def get_match_methods(self) -> List[str]:
        """
        Returns a list of match methods supported by the matcher.

        :return: List of supported match methods
        """
        return get_match_methods(self._base_url)

    def get_match_modes(self) -> List[str]:
        """
        Returns a list of match modes supported by the matcher.

        :return: List of supported match modes
        """
        return get_match_modes(self._base_url)

    def match(
            self,
            config: MatchConfiguration,
            domain_list: List[str],
            range_list: List[str]
    ) -> List[MatchResult]:
        """
        Computes the similarity between a list of domain and range bit vectors using the
        provided match configuration.

        :param config: Match configuration
        :param domain_list: List of domain bit vectors
        :param range_list: List of range bit vectors
        :return: Computed similarities according to match configuration
        """
        return match(self._base_url, config, domain_list, range_list)
