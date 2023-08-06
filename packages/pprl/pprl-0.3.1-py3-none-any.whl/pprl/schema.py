"""
This module contains functions for converting arbitrary objects into model classes
used by the PPRL package and back. None of the functions are exposed, since they are for
internal use only.
"""

from typing import Dict, Any, Optional

from .model import MatchConfiguration, BitVectorMetadataSpecification, SessionCancellation, \
    BitVectorMetadata, BitVector, BitVectorMatch, BloomFilterConfiguration, AttributeSchema, Entity, EncodedEntity, \
    MatchResult

JsonObject = Dict[str, Any]


def _set_if_not_none(d: JsonObject, attr: str, val: Optional[Any]):
    if val is not None:
        d[attr] = val


def _serialize_match_configuration(config: MatchConfiguration) -> JsonObject:
    d = {}

    _set_if_not_none(d, "matchFunction", config.match_function)
    _set_if_not_none(d, "matchMode", config.match_mode)
    _set_if_not_none(d, "threshold", config.threshold)

    return d


def _serialize_metadata_specification(spec: BitVectorMetadataSpecification) -> JsonObject:
    return {
        "name": spec.name,
        "dataType": spec.data_type,
        "decisionRule": spec.decision_rule
    }


def _serialize_session_cancellation(cancel: SessionCancellation) -> JsonObject:
    d = {"strategy": cancel.strategy}
    d.update({
        k: str(v) for k, v in cancel.options.items()
    })

    return d


def _serialize_bit_vector_metadata(meta: BitVectorMetadata) -> JsonObject:
    return {
        "name": meta.name,
        "value": meta.value
    }


def _deserialize_bit_vector_metadata(json_data: JsonObject) -> BitVectorMetadata:
    return BitVectorMetadata(
        name=json_data["name"],
        value=json_data["value"]
    )


def _serialize_bit_vector(vector: BitVector) -> JsonObject:
    return {
        "id": vector.id,
        "value": vector.value,
        "metadata": [
            _serialize_bit_vector_metadata(m) for m in vector.metadata
        ]
    }


def _deserialize_bit_vector(json_data: JsonObject) -> BitVector:
    return BitVector(
        id=json_data["id"],
        value=json_data["value"],
        metadata=[
            _deserialize_bit_vector_metadata(m) for m in json_data["metadata"]
        ]
    )


def _deserialize_secret_response(json_data: JsonObject) -> str:
    return json_data["secret"]


def _deserialize_progress_response(json_data: JsonObject) -> float:
    return json_data["progress"]


def _deserialize_bit_vector_match(json_data: JsonObject) -> BitVectorMatch:
    return BitVectorMatch(
        vector=_deserialize_bit_vector(json_data["vector"]),
        similarity=json_data["similarity"],
        reference_metadata=[
            _deserialize_bit_vector_metadata(m) for m in json_data["referenceMetadata"]
        ]
    )


def _serialize_bloom_filter_config(config: BloomFilterConfiguration) -> JsonObject:
    d = {}

    _set_if_not_none(d, "charset", config.charset)
    _set_if_not_none(d, "filterType", config.filter_type)
    _set_if_not_none(d, "hashStrategy", config.hash_strategy)
    _set_if_not_none(d, "hashValues", config.hash_values)
    _set_if_not_none(d, "tokenSize", config.token_size)
    _set_if_not_none(d, "seed", config.seed)
    _set_if_not_none(d, "key", config.key)
    _set_if_not_none(d, "salt", config.salt)

    return d


def _serialize_attribute_schema(schema: AttributeSchema) -> JsonObject:
    return {
        "attributeName": schema.attribute_name,
        "dataType": schema.data_type,
        "averageTokenCount": schema.average_token_count,
        "weight": schema.weight
    }


def _serialize_entity(entity: Entity) -> JsonObject:
    e = {"id": entity.id}

    for k, v in entity.attributes.items():
        e[k] = str(v)

    return e


def _deserialize_encoded_entity(json_data: JsonObject) -> EncodedEntity:
    return EncodedEntity(
        id=json_data["id"],
        value=json_data["value"]
    )


def _deserialize_match_result(json_data: JsonObject) -> MatchResult:
    return MatchResult(
        domain=json_data["domain"],
        range=json_data["range"],
        similarity=json_data["confidence"]
    )
