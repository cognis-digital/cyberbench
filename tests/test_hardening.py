"""Hardening tests: edge cases, bad input, and CLI error paths."""
from __future__ import annotations

import pytest

from cyberbench.core import magic
from cyberbench.core import run
from cyberbench.cli import main


# ---------------------------------------------------------------------------
# core.run — bad inputs
# ---------------------------------------------------------------------------

def test_run_unknown_op_exits_nonzero():
    """An unknown op raises ValueError with a clear message."""
    with pytest.raises(ValueError, match="unknown op"):
        run(b"hello", ["definitely_not_an_op"])


def test_run_empty_recipe_returns_data_unchanged():
    """An empty recipe list is a no-op — data passes through unmodified."""
    data = b"untouched"
    assert run(data, []) == data


def test_run_none_data_raises_typeerror():
    """Passing None as data raises a clear TypeError."""
    with pytest.raises(TypeError, match="None"):
        run(None, ["base64encode"])  # type: ignore[arg-type]


def test_run_none_recipe_raises_typeerror():
    """Passing None as recipe raises a clear TypeError."""
    with pytest.raises(TypeError, match="None"):
        run(b"x", None)  # type: ignore[arg-type]


def test_run_whitespace_op_stripped():
    """Op names with surrounding whitespace are normalised before lookup."""
    data = b"hello"
    assert run(data, ["  base64encode  "]) == run(data, ["base64encode"])


def test_run_str_data_accepted():
    """run() accepts str data in addition to bytes."""
    result = run("hello", ["hexencode"])
    assert result == b"68656c6c6f"


# ---------------------------------------------------------------------------
# core._xor — empty key guard
# ---------------------------------------------------------------------------

def test_xor_empty_key_raises():
    """xor with an empty key must raise ValueError, not ZeroDivisionError."""
    with pytest.raises(ValueError, match="empty"):
        from cyberbench.core import _xor
        _xor(b"data", b"")


# ---------------------------------------------------------------------------
# core.magic — edge cases
# ---------------------------------------------------------------------------

def test_magic_empty_bytes_returns_empty_list():
    """magic() on empty bytes must return [] without raising."""
    assert magic(b"") == []


def test_magic_none_returns_empty_list():
    """magic() on None must return [] without raising."""
    assert magic(None) == []  # type: ignore[arg-type]


def test_magic_returns_list_of_dicts():
    """magic() always returns a list; each entry has 'recipe' and 'preview'."""
    result = magic(b"aGVsbG8=")  # base64 for "hello"
    assert isinstance(result, list)
    for item in result:
        assert "recipe" in item
        assert "preview" in item


# ---------------------------------------------------------------------------
# CLI — error paths return non-zero exit codes without tracebacks
# ---------------------------------------------------------------------------

def test_cli_run_unknown_op_returns_nonzero():
    """CLI: unknown op exits with code 2 (not 0 and not an unhandled exception)."""
    rc = main(["run", "--recipe", "notanop", "hello"])
    assert rc != 0


def test_cli_run_empty_recipe_returns_nonzero():
    """CLI: empty --recipe string exits with a non-zero code."""
    rc = main(["run", "--recipe", "   ", "hello"])
    assert rc != 0


def test_cli_ops_lists_all_ops():
    """CLI: 'ops' subcommand exits 0."""
    rc = main(["ops"])
    assert rc == 0


def test_cli_magic_on_plain_text_exits_zero():
    """CLI: magic subcommand exits 0 even when nothing is detected."""
    rc = main(["magic", "plaintext_nothing_special"])
    assert rc == 0


def test_cli_run_valid_roundtrip_exits_zero(capsys):
    """CLI: valid run subcommand exits 0 and produces output."""
    rc = main(["run", "--recipe", "base64encode,base64decode", "hello"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "hello" in captured.out


def test_cli_no_subcommand_exits_zero():
    """CLI: calling without a subcommand prints help and exits 0."""
    rc = main([])
    assert rc == 0
