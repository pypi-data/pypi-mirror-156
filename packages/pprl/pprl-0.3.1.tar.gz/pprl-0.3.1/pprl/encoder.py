"""
This module contains functions for interacting with the PPRL encoder service
provided by the Medical Data Science Group Leipzig.
"""

from typing import List

import requests

from .model import ApiError, BloomFilterConfiguration, AttributeSchema, Entity, EncodedEntity
from .schema import _serialize_bloom_filter_config, _serialize_attribute_schema, _serialize_entity, \
    _deserialize_encoded_entity
from .util import _append_path, _check_response_errors, GenericRestClient


def get_hash_strategies(base_url: str) -> List[str]:
    """
    Returns a list of hash strategies supported by the encoder.

    :param base_url: Encoder service base URL
    :return: List of supported hash strategies
    """
    url = _append_path(base_url, "hash-strategies")
    r = requests.get(url)

    if r.status_code != requests.codes.ok:
        raise ApiError("Couldn't fetch hash strategies", r.status_code)

    return r.json()


def encode(
        base_url: str,
        config: BloomFilterConfiguration,
        schema_list: List[AttributeSchema],
        entity_list: List[Entity]
) -> List[EncodedEntity]:
    """
    Encodes a list of entities into bit vectors.

    :param base_url: Encoder service base URL
    :param config: Bloom filter configuration
    :param schema_list: List of attribute schemas
    :param entity_list: List of entities
    :return: List of encoded entities
    """
    if len(entity_list) == 0:
        return []

    url = _append_path(base_url, "encode")
    r = requests.post(url, json={
        "bloomFilter": _serialize_bloom_filter_config(config),
        "schemas": [
            _serialize_attribute_schema(s) for s in schema_list
        ],
        "entities": [
            _serialize_entity(e) for e in entity_list
        ]
    })

    _check_response_errors(r, requests.codes.ok, {
        requests.codes.bad_request: "Invalid encoder configuration"
    })

    return [
        _deserialize_encoded_entity(e) for e in r.json()["entities"]
    ]


class EncoderClient(GenericRestClient):
    """
    Wrapper around the API endpoints exposed by the encoder service.
    """

    def get_hash_strategies(self) -> List[str]:
        """
        Returns a list of hash strategies supported by the encoder.

        :return: List of supported hash strategies
        """
        return get_hash_strategies(self._base_url)

    def encode(
            self,
            config: BloomFilterConfiguration,
            schema_list: List[AttributeSchema],
            entity_list: List[Entity]
    ) -> List[EncodedEntity]:
        """
        Encodes a list of entities into bit vectors.

        :param config: Bloom filter configuration
        :param schema_list: List of attribute schemas
        :param entity_list: List of entities
        :return: List of encoded entities
        """
        return encode(self._base_url, config, schema_list, entity_list)
