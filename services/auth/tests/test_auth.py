from app.security import create_access_token, hash_password, verify_password
from mlp_common.jwt_utils import verify_token


def test_password_hash_roundtrip():
    digest = hash_password("a-long-password")
    assert verify_password("a-long-password", digest)
    assert not verify_password("wrong-password", digest)


def test_access_token_roundtrip():
    token = create_access_token("12345678-1234-1234-1234-123456789abc", "test-secret", 5)
    payload = verify_token(token, "test-secret")
    assert payload["sub"] == "12345678-1234-1234-1234-123456789abc"
