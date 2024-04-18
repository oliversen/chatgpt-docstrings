import lsprotocol.types as lsp

from log import log_to_output
from server import LSP_SERVER


def show_error(message: str) -> None:
    log_to_output(message, lsp.MessageType.Error)
    LSP_SERVER.show_message(message, lsp.MessageType.Error)


def show_warning(message: str) -> None:
    log_to_output(message, lsp.MessageType.Warning)
    LSP_SERVER.show_message(message, lsp.MessageType.Warning)


def show_info(message: str) -> None:
    log_to_output(message, lsp.MessageType.Info)
    LSP_SERVER.show_message(message, lsp.MessageType.Info)
