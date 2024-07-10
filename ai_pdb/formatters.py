from __future__ import annotations

import pprint
import re
from typing import TYPE_CHECKING

from ai_pdb.strings import (
    CONTEXT,
    DEBUG_PROMPT,
    DOCS_PROMPT,
    ERROR_INFO,
    QUERY_PROMPT,
    RESPONSE,
    SYSTEM_PROMPT,
)

if TYPE_CHECKING:
    from types import FrameType

    from anthropic.types import ContentBlock

    from ai_pdb.types import Command

command_map: dict[Command, str] = {
    "debug": DEBUG_PROMPT,
    "query": QUERY_PROMPT,
    "docs": DOCS_PROMPT,
}


class PromptFormatter:
    system: str = SYSTEM_PROMPT

    def format(
        self,
        command: Command,
        query: str | None,
        frame: FrameType | None,
        source_context: str,
        last_exception: dict | None,
    ) -> str:
        debugger_context = self._format_debugger_context(
            frame,
            source_context,
            last_exception,
        )

        prompt = command_map.get(command, DEBUG_PROMPT)

        formatted = prompt.format(debugger_context=debugger_context, query=query)

        return self._strip(formatted)

    def _format_debugger_context(
        self,
        frame: FrameType | None,
        code_context: str,
        last_exception: dict | None,
    ) -> str:
        if not frame:
            return "No active frame available for debugging."

        context = CONTEXT.format(
            filename=frame.f_code.co_filename,
            current_line=frame.f_lineno,
            function_name=frame.f_code.co_name,
            code_context=code_context,
            local_vars=pprint.pformat(frame.f_locals, indent=2),
            last_exception=self._format_exception(last_exception),
        )

        return context

    def _format_exception(self, last_exception: dict | None) -> str:
        if not last_exception:
            return "No error captured in the current debugging session."

        return ERROR_INFO.format(
            error_type=last_exception["type"],
            error_message=last_exception["value"],
            traceback=last_exception["traceback"],
        )

    def _strip(self, context: str) -> str:
        context = re.sub(r"[^\S\n]+", " ", context)
        context = re.sub(r"^ +", "", context, flags=re.MULTILINE)
        context = re.sub(r" +$", "", context, flags=re.MULTILINE)
        context = re.sub(r"\n\s*\n", "\n", context)

        return context.strip()


class ResponseFormatter:
    def format(self, response: list[ContentBlock]) -> str:
        width = 80
        separator = "*" * width

        formatted_response = RESPONSE.format(separator=separator)
        for message in response:
            if message.type == "tool_use":
                continue

            formatted_response += message.text + "\n\n"

        formatted_response += f"{separator}\n"

        return formatted_response
