from __future__ import annotations

import contextlib
import os
from asyncio import iscoroutinefunction
from functools import wraps
from typing import Any, Callable, Literal, TypeVar

import httpx
import lsprotocol.types as lsp
from openai import DefaultAsyncHttpxClient
from pygls.workspace import TextDocument

from .code_analyzers.base import CodeEntity, DocumentPosition
from .code_analyzers.factory import AnalyzerFactory
from .proxy import Proxy

F = TypeVar("F", bound=Callable)


def mark_as_feature(
    name: str,
    options: Any = None,  # noqa: ANN401
) -> Callable[[F], F]:
    """Decorator to mark a function as an LSP feature.

    This decorator adds metadata to a function, so that it can be registered
    as an LSP feature using the `DocstringLanguageServer.register_feature` method.

    Example:
        @mark_as_feature(name="hover", options={"supported_languages": ["python"]})
        def hover_feature():
            pass

        server.register_feature(hover_feature)
    """

    def decorator(f: F) -> F:
        f.future_name = name
        f.future_options = options
        return f

    return decorator


def mark_as_command(name: str) -> Callable[[F], F]:
    """Decorator to mark a function as a custom LSP command.

    This decorator adds metadata to a function, so that it can be registered
    as an LSP command using the `DocstringLanguageServer.register_command` method.

    Example:
        @mark_as_command('my_custom_command')
        def my_command():
            pass

        server.register_command(my_command)
    """

    def decorator(f: F) -> F:
        f.command_name = name
        return f

    return decorator


def stub_for_tests(return_value: Any) -> Callable:  # noqa: ANN401
    """Decorator to return a specified value in tests if PYTEST_CURRENT_TEST is set.

    Necessary for server testing because the server runs as a separate process.
    """

    def decorator(function: Callable) -> Callable:
        if iscoroutinefunction(function):

            @wraps(function)
            async def async_wrapper(*args, **kwargs) -> Any:  # noqa: ANN401
                if os.getenv("PYTEST_CURRENT_TEST"):
                    return return_value
                return await function(*args, **kwargs)

            return async_wrapper
        else:

            @wraps(function)
            def wrapper(*args, **kwargs) -> Any:  # noqa: ANN401
                if os.getenv("PYTEST_CURRENT_TEST"):
                    return return_value
                return function(*args, **kwargs)

            return wrapper

    return decorator


def get_entity_at_cursor(
    source_code: str, cursor: lsp.Position, analyzer_name: str = "jedi"
) -> CodeEntity | None:
    """Returns the code entity at the given cursor position in the document."""
    normalized_cursor = DocumentPosition.from_lsp(cursor)
    code_analyzer = AnalyzerFactory.create_analyzer(analyzer_name, source_code)
    code_entity = code_analyzer.get_context(normalized_cursor)
    return code_entity


def get_line_endings(lines: list[str]) -> Literal["\r\n", "\n"]:
    """Returns line endings used in the text."""
    with contextlib.suppress(IndexError):
        if lines[0][-2:] == "\r\n":
            return "\r\n"
    return "\n"


def match_line_endings(document: TextDocument, text: str) -> str:
    """Ensures that the edited text line endings matches the document line endings."""
    expected = get_line_endings(document.source.splitlines(keepends=True))
    actual = get_line_endings(text.splitlines(keepends=True))
    if actual == expected or actual is None or expected is None:
        return text
    return text.replace(actual, expected)


def create_httpx_client(proxy: Proxy | None) -> DefaultAsyncHttpxClient:
    """Creates openai.DefaultAsyncHttpxClient based on the proxy settings."""
    if proxy is None:
        client = DefaultAsyncHttpxClient()
    else:
        if proxy.url.startswith("https://"):
            ssl_context = httpx.create_ssl_context(proxy.strict_ssl)
        else:
            ssl_context = None
        headers = {"Proxy-Authorization": proxy.authorization}
        client = DefaultAsyncHttpxClient(
            proxy=httpx.Proxy(
                proxy.url,
                headers=headers,
                ssl_context=ssl_context,
            ),
        )
    return client
