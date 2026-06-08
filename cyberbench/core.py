"""cyberbench core — chainable encode/decode/transform (CyberChef-style), stdlib only."""
from __future__ import annotations
import base64, binascii, codecs, gzip, html, urllib.parse, json
TOOL_NAME = "cyberbench"; TOOL_VERSION = "1.0.0"

def _b64e(b): return base64.b64encode(b)
def _b64d(b): return base64.b64decode(b + b"=" * (-len(b) % 4))
def _hexe(b): return binascii.hexlify(b)
def _hexd(b): return binascii.unhexlify(b.replace(b" ", b""))
def _urle(b): return urllib.parse.quote_from_bytes(b).encode()
def _urld(b): return urllib.parse.unquote_to_bytes(b.decode("utf-8", "replace"))
def _rot13(b): return codecs.encode(b.decode("utf-8", "replace"), "rot_13").encode()
def _gze(b): return gzip.compress(b)
def _gzd(b): return gzip.decompress(b)
def _xor(b, key=b"K"): return bytes(c ^ key[i % len(key)] for i, c in enumerate(b))
def _htmle(b): return html.escape(b.decode("utf-8", "replace")).encode()
def _htmld(b): return html.unescape(b.decode("utf-8", "replace")).encode()

OPS = {"base64encode": _b64e, "base64decode": _b64d, "hexencode": _hexe, "hexdecode": _hexd,
       "urlencode": _urle, "urldecode": _urld, "rot13": _rot13, "gzip": _gze, "gunzip": _gzd,
       "xor": _xor, "htmlencode": _htmle, "htmldecode": _htmld}

def run(data, recipe):
    """Apply a list of op names to bytes `data` left-to-right. Returns bytes."""
    if isinstance(data, str): data = data.encode()
    for op in recipe:
        op = op.strip().lower()
        if op not in OPS: raise ValueError(f"unknown op: {op} (have: {', '.join(sorted(OPS))})")
        data = OPS[op](data)
    return data

def magic(data):
    """Try to auto-decode common encodings; return list of (recipe, preview)."""
    if isinstance(data, str): data = data.encode()
    out = []
    for name, fn in (("base64decode", _b64d), ("hexdecode", _hexd), ("urldecode", _urld), ("rot13", _rot13), ("gunzip", _gzd)):
        try:
            r = fn(data); txt = r.decode("utf-8", "strict")
            if txt.isprintable(): out.append({"recipe": name, "preview": txt[:120]})
        except Exception:
            pass
    return out
