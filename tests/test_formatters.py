from unittest.mock import Mock

import pytest

from ai_pdb.formatters import PromptFormatter


@pytest.fixture()
def formatter():
    return PromptFormatter()


@pytest.fixture()
def frame():
    frame = Mock()
    frame.f_code = Mock()
    frame.f_lineno = 10
    frame.f_locals = {"var": "value"}

    return frame


def test_format_with_debug_command(formatter):
    result = formatter.format("debug", None, None, "def foo(): pass", None)

    assert (
        result
        == "Command: debug\nHere's the current debugging context:\nNo active frame available for debugging.\nBased on this context, please provide your analysis and any relevant advice. Suggest a fix for the Last Error, if any."  # noqa: E501
    )


def test_format_with_query_command(formatter):
    result = formatter.format("query", "test query", None, "def foo(): pass", None)

    assert "No active frame available for debugging." in result
    assert "test query" in result


def test_format_debugger_context_with_frame(formatter, frame):
    result = formatter.format("debug", None, frame, "def foo(): pass", None)

    assert "def foo(): pass" in result
    assert "var" in result


def test_format_exception_with_exception(formatter, frame):
    exception = {
        "type": "TypeError",
        "value": "An error occurred",
        "traceback": "Traceback details",
    }

    result = formatter.format("debug", None, frame, "def foo(): pass", exception)

    assert "TypeError" in result
    assert "An error occurred" in result
    assert "Traceback details" in result


def test_format_exception_with_none_exception(formatter, frame):
    result = formatter.format("debug", None, frame, "def foo(): pass", None)

    assert "No error captured in the current debugging session." in result
