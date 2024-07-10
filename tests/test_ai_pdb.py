from unittest.mock import MagicMock, patch

import pytest

from ai_pdb import AIPdb


@pytest.fixture
def ai_pdb():
    return AIPdb()


def test_capture_exception(ai_pdb):
    try:
        raise ValueError("Test exception")
    except Exception as e:
        exc_type, exc_value, exc_traceback = type(e), e, e.__traceback__
        ai_pdb.capture_exception(exc_type, exc_value, exc_traceback)

    assert ai_pdb.last_exception is not None
    assert ai_pdb.last_exception["type"] == "ValueError"
    assert ai_pdb.last_exception["value"] == "Test exception"
    assert "test_capture_exception" in ai_pdb.last_exception["traceback"]


def test_get_context(ai_pdb):
    with patch("inspect.getsource") as mock_getsource:
        mock_frame = MagicMock()
        mock_getsource.return_value = "def foo(): pass"
        ai_pdb.curframe = mock_frame

        context = ai_pdb.get_context()

        mock_getsource.assert_called_once_with(mock_frame.f_code)
        assert context == "def foo(): pass"


def test_get_command(ai_pdb):
    assert ai_pdb.get_command([]) == "debug"
    assert ai_pdb.get_command(["debug"]) == "debug"
    assert ai_pdb.get_command(["docs"]) == "docs"
    assert ai_pdb.get_command(["query"]) == "query"

    with pytest.raises(ValueError):
        ai_pdb.get_command(["invalid"])


@pytest.mark.parametrize(
    "arg, expected_command, expected_query",
    [
        ("", "debug", None),
        ("debug", "debug", None),
        ("docs", "docs", None),
        ("query Why does this even work?", "query", "Why does this even work?"),
    ],
)
def test_do_ai_command_parsing(ai_pdb, arg, expected_command, expected_query):
    with patch.object(ai_pdb, "query_ai") as mock_query_ai, patch.object(
        ai_pdb, "response_formatter"
    ) as mock_formatter, patch("builtins.print") as mock_print:
        mock_query_ai.return_value.content = ["Test response"]
        mock_formatter.format.return_value = "Formatted response"

        ai_pdb.do_ai(arg)

        mock_query_ai.assert_called_once_with(expected_command, expected_query)
        mock_formatter.format.assert_called_once_with(["Test response"])
        mock_print.assert_called_once_with("Formatted response")


def test_query_ai(ai_pdb):
    with patch.object(ai_pdb, "client") as mock_client, patch.object(
        ai_pdb, "prompt_formatter"
    ) as mock_prompt_formatter, patch("inspect.getsource") as mock_getsource:
        ai_pdb.curframe = MagicMock()
        mock_getsource.return_value = "def foo(): pass"
        mock_client.messages.create.return_value = MagicMock(content="AI response")
        mock_prompt_formatter.format.return_value = "formatted prompt"

        response = ai_pdb.query_ai("debug")

        mock_prompt_formatter.format.assert_called_once()
        mock_client.messages.create.assert_called_once_with(
            max_tokens=1024,
            messages=[{"role": "user", "content": "formatted prompt"}],
            model="claude-3-5-sonnet-20240620",
            system=mock_prompt_formatter.system,
        )
        assert response.content == "AI response"
