import time
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from ai_pdb.spinner import Spinner


@pytest.fixture
def spinner():
    return Spinner("Testing")


def test_spinner_init(spinner):
    assert spinner.message == "Testing"
    assert spinner.delay == 0.1
    assert not spinner.running
    assert spinner.spinner_thread is None


@patch("sys.stdout", new_callable=StringIO)
def test_spinner_integration(mock_stdout):
    with patch("threading.Thread", MagicMock()) as mock_thread:
        spinner = Spinner("Integration Test")
        spinner.start()
        time.sleep(0.5)  # Simulate some work
        spinner.stop()

        mock_thread.assert_called_once_with(target=spinner.spin)
        mock_thread.return_value.start.assert_called_once()
        assert mock_stdout.getvalue().endswith(
            "\r" + " " * (len(spinner.message) + 10) + "\r"
        )


def test_spinner_context_manager():
    with patch("sys.stdout", new_callable=StringIO) as mock_stdout, patch(
        "threading.Thread", MagicMock()
    ) as mock_thread, patch("time.sleep", return_value=None):
        with Spinner("Context Test") as spinner:
            time.sleep(0.5)  # Simulate some work

        mock_thread.assert_called_once_with(target=spinner.spin)
        mock_thread.return_value.start.assert_called_once()
        assert not spinner.running
        assert mock_stdout.getvalue().endswith(
            "\r" + " " * (len(spinner.message) + 10) + "\r"
        )
