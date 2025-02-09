from __future__ import annotations

import enum
from typing import Callable

import lsprotocol.types as lsp
from attr import dataclass
from pygls.server import LanguageServer

from commands import apply_generate_docstring
from completions import completions
from initialize import initialize
from settings import SERVER_NAME, SERVER_VERSION, GlobalSettings, WorkspaceSettings


@enum.unique
class TelemetryType(str, enum.Enum):
    """Represents telemetry type."""

    Info = "info"
    Error = "error"


@dataclass
class TelemetryParams:
    """Represents telemetry parameters."""

    type: TelemetryType  # noqa: A003
    name: str
    data: dict


class DocstringLanguageServer(LanguageServer):
    """A custom LanguageServer implementation."""

    global_settings: GlobalSettings
    workspace_settings: WorkspaceSettings

    def register_feature(self, function: Callable) -> None:
        """Register a function as an LSP feature.

        This method accepts a function that has been decorated
        with the `utils.mark_as_feature` decorator.

        Example:
            @mark_as_feature(name="hover", options={"supported_languages": ["python"]})
            def hover_feature():
                pass

            server.register_feature(hover_feature)
        """
        self.feature(function.future_name, function.future_options)(function)

    def register_command(self, function: Callable) -> None:
        """Registers a function as a custom LSP command.

        This method accepts a function that has been decorated
        with the `utils.mark_as_command` decorator.

        Example:
            @mark_as_command('my_custom_command')
            def my_command():
                pass

            server.register_command(my_command)
        """
        self.command(function.command_name)(function)

    def log_to_output(
        self, message: str, msg_type: lsp.MessageType = lsp.MessageType.Log
    ) -> None:
        """Logs a message to the output channel."""
        self.show_message_log(message, msg_type)

    def show_error(self, message: str) -> None:
        """Displays an error notification and logs it to the output channel."""
        self.log_to_output(message, lsp.MessageType.Error)
        self.show_message(message, lsp.MessageType.Error)

    def show_warning(self, message: str) -> None:
        """Displays a warning notification and logs it to the output channel."""
        self.log_to_output(message, lsp.MessageType.Warning)
        self.show_message(message, lsp.MessageType.Warning)

    def show_info(self, message: str) -> None:
        """Displays an info notification and logs it to the output channel."""
        self.log_to_output(message, lsp.MessageType.Info)
        self.show_message(message, lsp.MessageType.Info)

    def _send_telemetry(self, params: TelemetryParams) -> None:
        """Sends telemetry data."""
        self.send_notification(lsp.TELEMETRY_EVENT, params)

    def send_telemetry_info(self, name: str, data: dict[str, str]) -> None:
        """Sends informational telemetry data."""
        params = TelemetryParams(TelemetryType.Info, name, data)
        self._send_telemetry(params)

    def send_telemetry_error(self, name: str, data: dict[str, str]) -> None:
        """Sends error telemetry data."""
        params = TelemetryParams(TelemetryType.Error, name, data)
        self._send_telemetry(params)


def create_server() -> DocstringLanguageServer:
    """Creates DocstringLanguageServer instance."""
    server = DocstringLanguageServer(name=SERVER_NAME, version=SERVER_VERSION)
    server.register_feature(initialize)
    server.register_feature(completions)
    server.register_command(apply_generate_docstring)
    return server
