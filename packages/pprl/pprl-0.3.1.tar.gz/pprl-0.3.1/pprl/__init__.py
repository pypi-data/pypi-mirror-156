"""
This package contains functions for using the PPRL services provided by the
Medical Data Science Group Leipzig. More specifically, the functions offered in this
package are wrappers around the REST APIs of the encoder, match and broker service respectively.
"""

__version__ = '0.3.1'

from . import broker, encoder, match
from .model import (
    ApiError,
    MatchConfiguration,
    SessionCancellation,
    BitVectorMetadata,
    BitVectorMetadataSpecification,
    BitVector,
    BitVectorMatch,
    BloomFilterConfiguration,
    AttributeSchema,
    Entity,
    EncodedEntity,
    MatchResult
)
