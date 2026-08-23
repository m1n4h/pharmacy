"""
Unit Tests — Security, JWT, Password, Utilities
"""
import time
import pytest
from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token, create_refresh_token, decode_token
from app.core.security_utils import SecurityUtils


# ---- Password Hashing ----

class TestPasswordHashing:

    def test_hash_password_returns_string(self):
        h = hash_password("Test123!")
        assert isinstance(h, str)
        assert len(h) > 0

    def test_verify_password_correct(self):
        plain = "MySecurePass1!"
        h = hash_password(plain)
        assert verify_password(plain, h) is True

    def test_verify_password_wrong(self):
        h = hash_password("CorrectPass1!")
        assert verify_password("WrongPass1!", h) is False

    def test_same_password_different_hashes(self):
        h1 = hash_password("SamePass1!")
        h2 = hash_password("SamePass1!")
        assert h1 != h2  # bcrypt salts differ each time

    def test_empty_password(self):
        h = hash_password("")
        assert isinstance(h, str)
        assert verify_password("", h) is True

    def test_long_password(self):
        long_p = "A" * 200 + "1!"
        h = hash_password(long_p)
        assert verify_password(long_p, h) is True


# ---- JWT ----

class TestJWT:

    def test_create_access_token_returns_tuple(self):
        token, expires_in = create_access_token({"sub": "test@test.com", "role": "staff"})
        assert isinstance(token, str)
        assert isinstance(expires_in, (int, float))
        assert expires_in > 0

    def test_decode_token_valid(self):
        data = {"sub": "user@test.com", "role": "admin"}
        token, _ = create_access_token(data)
        decoded = decode_token(token)
        assert decoded["sub"] == "user@test.com"
        assert decoded["role"] == "admin"

    def test_decode_token_expired(self):
        from app.core.config import get_settings
        from datetime import datetime, timedelta
        from jose import jwt
        settings = get_settings()
        expired = datetime.utcnow() - timedelta(seconds=10)
        token = jwt.encode(
            {"sub": "test@test.com", "role": "staff", "exp": expired, "type": "access"},
            settings.secret_key,
            algorithm="HS256"
        )
        with pytest.raises(Exception):
            decode_token(token)

    def test_decode_token_invalid(self):
        with pytest.raises(Exception):
            decode_token("this.is.not.a.valid.token")

    def test_create_refresh_token(self):
        rt = create_refresh_token()
        assert isinstance(rt, str)
        assert len(rt) > 20

    def test_access_token_contains_claims(self):
        token, _ = create_access_token({"sub": "a@b.com", "role": "pharmacist"})
        decoded = decode_token(token)
        assert "sub" in decoded
        assert "role" in decoded
        assert decoded["role"] == "pharmacist"


# ---- SecurityUtils ----

class TestSecurityUtils:

    def test_generate_secure_token(self):
        t = SecurityUtils.generate_secure_token()
        assert isinstance(t, str)
        assert len(t) > 20

    def test_hash_token(self):
        h = SecurityUtils.hash_token("abc123")
        assert isinstance(h, str)
        assert len(h) == 64  # SHA-256 hex

    def test_hash_token_consistent(self):
        h1 = SecurityUtils.hash_token("same_input")
        h2 = SecurityUtils.hash_token("same_input")
        assert h1 == h2

    def test_validate_password_strength_valid(self):
        valid, msg = SecurityUtils.validate_password_strength("StrongP@ss1")
        assert valid is True

    def test_validate_password_too_short(self):
        valid, msg = SecurityUtils.validate_password_strength("Sh@1")
        assert valid is False

    def test_validate_password_no_uppercase(self):
        valid, msg = SecurityUtils.validate_password_strength("lowercase@1")
        assert valid is False

    def test_validate_password_no_digit(self):
        valid, msg = SecurityUtils.validate_password_strength("NoDigit@abc")
        assert valid is False

    def test_validate_password_no_special(self):
        valid, msg = SecurityUtils.validate_password_strength("NoSpecial1A")
        assert valid is False

    def test_sanitize_input(self):
        result = SecurityUtils.sanitize_input("  hello world  ")
        assert result == "hello world"

    def test_sanitize_input_max_length(self):
        long_str = "a" * 2000
        result = SecurityUtils.sanitize_input(long_str, max_length=100)
        assert len(result) <= 100

    def test_is_suspicious_request_normal(self):
        assert SecurityUtils.is_suspicious_request("Mozilla/5.0", "https://pharmacy.com") is False

    def test_is_suspicious_request_scanner(self):
        assert SecurityUtils.is_suspicious_request("sqlmap/1.0", "") is True

    def test_is_suspicious_request_nikto(self):
        assert SecurityUtils.is_suspicious_request("nikto", "") is True
