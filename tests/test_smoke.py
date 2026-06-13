"""Smoke tests for CYBERBENCH."""
import base64
from cyberbench.core import run, magic, OPS, TOOL_NAME, TOOL_VERSION


def test_identity():
    assert TOOL_NAME and TOOL_VERSION


def test_run_base64_roundtrip():
    """base64encode then base64decode should return the original bytes."""
    original = b"Hello, CyberBench!"
    encoded = run(original, ["base64encode"])
    decoded = run(encoded, ["base64decode"])
    assert decoded == original


def test_run_hex_roundtrip():
    """hexencode then hexdecode should return the original bytes."""
    original = b"deadbeef"
    encoded = run(original, ["hexencode"])
    decoded = run(encoded, ["hexdecode"])
    assert decoded == original


def test_run_chained_ops():
    """Chaining multiple ops applies them left-to-right."""
    data = b"test"
    # base64encode then hexencode
    result = run(data, ["base64encode", "hexencode"])
    expected = base64.b64encode(b"test")
    import binascii
    assert result == binascii.hexlify(expected)


def test_run_unknown_op_raises():
    """An unknown op name should raise ValueError."""
    import pytest
    with pytest.raises(ValueError, match="unknown op"):
        run(b"x", ["notanop"])


def test_run_accepts_str_input():
    """run() should accept str input as well as bytes."""
    result = run("hello", ["base64encode"])
    assert result == base64.b64encode(b"hello")


def test_magic_detects_base64():
    """magic() should detect base64-decodable printable content."""
    encoded = base64.b64encode(b"cyberbench magic works")
    results = magic(encoded)
    assert any(r["recipe"] == "base64decode" for r in results)
    assert any("cyberbench magic works" in r["preview"] for r in results)


def test_all_ops_present():
    """OPS dict must contain at least the standard encode/decode pairs."""
    required = {"base64encode", "base64decode", "hexencode", "hexdecode",
                "urlencode", "urldecode", "rot13", "gzip", "gunzip", "xor",
                "htmlencode", "htmldecode"}
    assert required.issubset(set(OPS))


def test_cli_importable():
    from cyberbench.cli import main
    assert callable(main)
