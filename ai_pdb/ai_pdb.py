from __future__ import annotations

import inspect
import os
import pdb
import shlex
import traceback
from typing import TYPE_CHECKING, cast

from anthropic import Anthropic

from ai_pdb.formatters import PromptFormatter, ResponseFormatter
from ai_pdb.spinner import Spinner
from ai_pdb.types import Command

if TYPE_CHECKING:
    from anthropic.types import Message


class AIPdb(pdb.Pdb):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = Anthropic()
        self.last_exception = None
        self.prompt_formatter = PromptFormatter()
        self.response_formatter = ResponseFormatter()

    def user_exception(self, frame, exc_info):
        self.capture_exception(*exc_info)
        return super().user_exception(frame, exc_info)

    def dispatch_exception(self, frame, arg):
        self.capture_exception(*arg)
        return super().dispatch_exception(frame, arg)

    def capture_exception(self, exc_type, exc_value, exc_traceback):
        self.last_exception = {
            "type": exc_type.__name__,
            "value": str(exc_value),
            "traceback": "".join(traceback.format_tb(exc_traceback)),
        }

    def do_ai(self, arg: str) -> None:
        """Handle the 'ai' command with optional arguments.
        Usage: ai [command] [args...]
        Commands:
            debug - Debug the current context and suggest a fix for the last exception,
                    if any
            docs - Display documentation relevant to the current context
            query <custom query> - Ask a custom query about the current context
            (empty) - Same as debug
        """
        args = shlex.split(arg)
        command = self.get_command(args)
        query = None

        if command == "query":
            query = " ".join(args[1:])

        with Spinner("Querying Claude..."):
            ai_response = self.query_ai(command, query)

        print(self.response_formatter.format(ai_response.content))

        self.last_exception = None

    def get_command(self, args: list[str]) -> Command:
        if not args:
            return "debug"

        cmd = args[0].lower()
        if cmd in ("debug", "query", "docs"):
            return cast(Command, cmd)

        raise ValueError(f"Invalid command: {cmd}")

    def query_ai(self, command: Command = "debug", query: str | None = None) -> Message:
        content = self.prompt_formatter.format(
            command,
            query,
            self.curframe,
            self.get_context(),
            self.last_exception,
        )

        if os.getenv("DEBUG"):
            print(content)

        return self.client.messages.create(
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": content,
                },
            ],
            model="claude-3-5-sonnet-20240620",
            system=self.prompt_formatter.system,
        )

    def get_context(self) -> str:
        frame = self.curframe
        if not frame:
            return ""

        return inspect.getsource(frame.f_code)
