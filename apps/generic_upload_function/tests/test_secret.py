from ..core.secret import verify_shared_secret
import hashlib
import pytest


def test_verify_ok():
    secret = 'abc123'
    h = hashlib.sha256(secret.encode()).hexdigest()
    verify_shared_secret(secret, h)  # should not raise


def test_verify_fail():
    secret = 'abc123'
    h = hashlib.sha256('different'.encode()).hexdigest()
    with pytest.raises(Exception):
        verify_shared_secret(secret, h)


def test_bypass_mode_allows_missing():
    # Should not raise even though provided secret is None and hash mismatches
    verify_shared_secret(None, 'deadbeef'*8, bypass=True)
