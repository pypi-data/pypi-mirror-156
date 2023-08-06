"""
This module contains model classes that are used throughout the PPRL package.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any


class ApiError(ConnectionError):

    def __init__(self, message: str, code: int):
        """
        Constructs a generic error message representing that the returned status code of an API did not match
        the expected status code.

        :param message: Error message
        :param code: Status code returned by the API
        """
        super().__init__(self, message)
        self.message = message
        self.code = code

    def __str__(self):
        return f"{self.message}: service returned status code {self.code}"


@dataclass(frozen=True)
class MatchConfiguration:
    """
    Collection of parameters for computing bit vector similarities.
    """
    match_function: Optional[str] = None
    """Similarity function to use (e.g. Dice, Jaccard, Cosine)"""
    match_mode: Optional[str] = None
    """Match mode to use (e.g. crosswise, pairwise)"""
    threshold: Optional[float] = None
    """Similarity threshold to distinguish match and non-match"""


@dataclass(frozen=True)
class SessionCancellation:
    """
    Collection of parameters for defining a way for a session to be cancelled.
    """
    strategy: str
    """Cancellation strategy (e.g. Simple, Token, Timeout)"""
    options: Dict[str, object] = field(default_factory=dict)
    """Cancellation strategy options (depend on chosen strategy)"""


@dataclass(frozen=True)
class BitVectorMetadata:
    """
    Metadata attached to a bit vector.
    """
    name: str
    """Metadata name"""
    value: str
    """Metadata value"""


@dataclass(frozen=True)
class BitVectorMetadataSpecification:
    """
    Specification of metadata that should be attached to a bit vector.
    """
    name: str
    """Metadata name"""
    data_type: str
    """Metadata datatype (e.g. str, int)"""
    decision_rule: str
    """Metadata ordering/decision rule (e.g. keepLatest, keepHighest)"""


@dataclass(frozen=True)
class BitVector:
    """
    Identifiable bit vector with additional metadata.
    """
    id: str
    """Bit vector ID"""
    value: str
    """Bit vector value"""
    metadata: List[BitVectorMetadata] = field(default_factory=list)
    """List of metadata attached to bit vector"""


@dataclass(frozen=True)
class BitVectorMatch:
    """
    Bit vector that has been matched against another bit vector.
    """
    vector: BitVector
    """Matched bit vector"""
    similarity: float
    """Similarity to other vector"""
    reference_metadata: List[BitVectorMetadata] = field(default_factory=list)
    """Metadata of matched bit vector, evaluated according to metadata decision rule"""


@dataclass(frozen=True)
class BloomFilterConfiguration:
    """
    Collection of Bloom filter encoding configuration options.
    """
    charset: Optional[str] = None
    """Character set to apply to incoming data"""
    filter_type: Optional[str] = None
    """Filter type to use (e.g. RBF, CLKRBF)"""
    hash_strategy: Optional[str] = None
    """Hash strategy to use (e.g. RANDOM_SHA256)"""
    hash_values: Optional[int] = None
    """Amount of hash values to compute"""
    token_size: Optional[int] = None
    """Size of text tokens"""
    seed: Optional[int] = None
    """Seed to use for RNG-based operations"""
    key: Optional[str] = None
    """Key to use for HMAC-based encoding"""
    salt: Optional[str] = None
    """Salt to prepend to text tokens"""


@dataclass(frozen=True)
class AttributeSchema:
    """
    Schema to apply to an entity attribute.
    """
    attribute_name: str
    """Name of attribute"""
    data_type: str
    """Datatype of attribute"""
    average_token_count: float
    """Average amount of tokens"""
    weight: float
    """Weight in encoding"""


@dataclass(frozen=True)
class Entity:
    """
    Data entity with arbitrary key-value attributes.
    """
    id: str
    """Entity ID"""
    attributes: Dict[str, Any] = field(default_factory=dict)
    """Entity attributes as key-value mapping"""


@dataclass(frozen=True)
class EncodedEntity:
    """
    Encoded data entity.
    """
    id: str
    """Entity ID"""
    value: str
    """Encoded entity attributes as bit vector"""


@dataclass(frozen=True)
class MatchResult:
    """
    Collection of information about matched bit vectors.
    """
    domain: str
    """Domain bit vector"""
    range: str
    """Range bit vector"""
    similarity: float
    """Similarity between domain and range bit vector"""
