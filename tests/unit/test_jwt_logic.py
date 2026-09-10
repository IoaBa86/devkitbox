from __future__ import annotations

import time

import pytest

from app.core.exceptions import ValidationError
from app.tools.jwt.logic import decode_jwt, encode_jwt

_KNOWN_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0."
    "dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
)


def test_decode_jwt_known_token():
    result = decode_jwt(_KNOWN_TOKEN)
    assert result.header == {"alg": "HS256", "typ": "JWT"}
    assert result.payload == {"sub": "1234567890", "name": "John Doe"}


def test_decode_jwt_wrong_segment_count_raises():
    with pytest.raises(ValidationError):
        decode_jwt("only.two")


def test_decode_jwt_invalid_base64_raises():
    with pytest.raises(ValidationError):
        decode_jwt("not-base64!.also-not.signature")


def test_decode_jwt_expired_token():
    token = encode_jwt({"exp": int(time.time()) - 3600}, "secret")
    result = decode_jwt(token)
    assert result.is_expired is True


def test_decode_jwt_not_yet_expired_token():
    token = encode_jwt({"exp": int(time.time()) + 3600}, "secret")
    result = decode_jwt(token)
    assert result.is_expired is False


def test_decode_jwt_no_exp_claim_is_expired_none():
    token = encode_jwt({"sub": "x"}, "secret")
    result = decode_jwt(token)
    assert result.is_expired is None


def test_encode_jwt_produces_three_segments():
    token = encode_jwt({"sub": "abc"}, "secret")
    assert len(token.split(".")) == 3


def test_encode_jwt_sets_alg_and_typ_header():
    token = encode_jwt({"sub": "abc"}, "secret", "HS384")
    result = decode_jwt(token)
    assert result.header == {"alg": "HS384", "typ": "JWT"}


def test_encode_jwt_round_trips_payload():
    payload = {"sub": "abc", "role": "admin", "n": 42}
    token = encode_jwt(payload, "secret")
    result = decode_jwt(token)
    assert result.payload == payload


def test_encode_jwt_deterministic_for_same_inputs():
    a = encode_jwt({"sub": "abc"}, "secret")
    b = encode_jwt({"sub": "abc"}, "secret")
    assert a == b


def test_encode_jwt_different_secret_different_signature():
    a = encode_jwt({"sub": "abc"}, "secret1")
    b = encode_jwt({"sub": "abc"}, "secret2")
    assert a.rsplit(".", 1)[0] == b.rsplit(".", 1)[0]  # same header+payload
    assert a != b  # different signature


def test_encode_jwt_empty_secret_raises():
    with pytest.raises(ValidationError):
        encode_jwt({"sub": "abc"}, "")


def test_encode_jwt_unsupported_algorithm_raises():
    with pytest.raises(ValidationError):
        encode_jwt({"sub": "abc"}, "secret", "RS256")


def test_encode_jwt_non_serializable_payload_raises():
    with pytest.raises(ValidationError):
        encode_jwt({"sub": object()}, "secret")
