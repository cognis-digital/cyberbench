"""cyberbench core — chainable encode/decode/transform (CyberChef-style), stdlib only."""
from __future__ import annotations

import base64
import binascii
import codecs
import gzip
import html
import urllib.parse

TOOL_NAME = "cyberbench"
TOOL_VERSION = "1.0.0"


def _b64e(b: bytes) -> bytes:
    return base64.b64encode(b)


def _b64d(b: bytes) -> bytes:
    return base64.b64decode(b + b"=" * (-len(b) % 4))


def _hexe(b: bytes) -> bytes:
    return binascii.hexlify(b)


def _hexd(b: bytes) -> bytes:
    return binascii.unhexlify(b.replace(b" ", b""))


def _urle(b: bytes) -> bytes:
    return urllib.parse.quote_from_bytes(b).encode()


def _urld(b: bytes) -> bytes:
    return urllib.parse.unquote_to_bytes(b.decode("utf-8", "replace"))


def _rot13(b: bytes) -> bytes:
    return codecs.encode(b.decode("utf-8", "replace"), "rot_13").encode()


def _gze(b: bytes) -> bytes:
    return gzip.compress(b)


def _gzd(b: bytes) -> bytes:
    return gzip.decompress(b)


def _xor(b: bytes, key: bytes = b"K") -> bytes:
    if not key:
        raise ValueError("xor key must not be empty")
    return bytes(c ^ key[i % len(key)] for i, c in enumerate(b))


def _htmle(b: bytes) -> bytes:
    return html.escape(b.decode("utf-8", "replace")).encode()


def _htmld(b: bytes) -> bytes:
    return html.unescape(b.decode("utf-8", "replace")).encode()


OPS: dict[str, object] = {
    "base64encode": _b64e,
    "base64decode": _b64d,
    "hexencode": _hexe,
    "hexdecode": _hexd,
    "urlencode": _urle,
    "urldecode": _urld,
    "rot13": _rot13,
    "gzip": _gze,
    "gunzip": _gzd,
    "xor": _xor,
    "htmlencode": _htmle,
    "htmldecode": _htmld,
}


def run(data: bytes | str, recipe: list[str]) -> bytes:
    """Apply a list of op names to bytes ``data`` left-to-right.  Returns bytes.

    Raises
    ------
    TypeError
        If *recipe* is not iterable or *data* is neither bytes nor str.
    ValueError
        If an op name is not recognised.
    """
    if data is None:
        raise TypeError("data must be bytes or str, got None")
    if not isinstance(data, (bytes, str)):
        raise TypeError(f"data must be bytes or str, got {type(data).__name__}")
    if isinstance(data, str):
        data = data.encode()
    if recipe is None:
        raise TypeError("recipe must be a list of op names, got None")
    for op in recipe:
        op = op.strip().lower()
        if op not in OPS:
            raise ValueError(f"unknown op: {op!r} (available: {', '.join(sorted(OPS))})")
        data = OPS[op](data)  # type: ignore[operator]
    return data


def magic(data: bytes | str) -> list[dict]:
    """Try to auto-decode common encodings; return list of {recipe, preview} dicts."""
    if data is None:
        return []
    if isinstance(data, str):
        data = data.encode()
    if not data:
        return []
    out = []
    candidates = [
        ("base64decode", _b64d),
        ("hexdecode", _hexd),
        ("urldecode", _urld),
        ("rot13", _rot13),
        ("gunzip", _gzd),
    ]
    for name, fn in candidates:
        try:
            r = fn(data)
            txt = r.decode("utf-8", "strict")
            if txt.isprintable():
                out.append({"recipe": name, "preview": txt[:120]})
        except Exception:
            pass
    return out
