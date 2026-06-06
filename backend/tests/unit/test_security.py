from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hashing():
    password = "testpassword123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_access_token():
    token = create_access_token("user123", "ws456", "owner")
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "user123"
    assert payload["workspace_id"] == "ws456"
    assert payload["role"] == "owner"
    assert payload["type"] == "access"


def test_refresh_token():
    token = create_refresh_token("user123")
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "user123"
    assert payload["type"] == "refresh"


def test_invalid_token():
    assert decode_token("invalid.token.here") is None
