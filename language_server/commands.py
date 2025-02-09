from __future__ import annotations

import asyncio
from concurrent.futures import Future
from typing import Awaitable, NamedTuple, TypedDict, cast

import lsprotocol.types as lsp
from pygls.workspace import TextDocument as LSPTextDocument

import server
from settings import ALLOWED_PROXY_PROTOCOLS
from utils import get_entity_at_cursor, mark_as_command, match_line_endings
from utils.code_analyzers.base import BaseFunction, CodeEntity
from utils.docstring import format_docstring, generate_docstring, parse_docstring
from utils.proxy import Proxy


class TextDocument(TypedDict):
    """Represents a text document."""

    uri: str


class Position(TypedDict):
    """Represents a position in a text document."""

    line: int
    character: int


class TextDocumentPosition(TypedDict):
    """Represents a text document and a position inside that document."""

    textDocument: TextDocument
    position: Position


class ProxySettings(TypedDict):
    """Represents settings for a proxy."""

    url: str
    authorization: str
    strictSSL: bool


class CommandArguments(NamedTuple):
    """Represents command arguments passed with an LSP request."""

    text_document_position: TextDocumentPosition
    api_key: str
    progress_token: lsp.ProgressToken


@mark_as_command("chatgpt-docstrings.applyGenerate")
async def apply_generate_docstring(
    ls: server.DocstringLanguageServer,
    args: tuple[TextDocumentPosition, str, lsp.ProgressToken],
) -> bool:
    """Generates a docstring and inserts it into the document."""
    uri, cursor, api_key, progress_token = _unpack_args(args)
    document = ls.workspace.get_text_document(uri)
    document_version = document.version or 0
    settings = ls.workspace_settings.get_settings_for_document(document)

    # Proxy setup and validation
    proxy = _create_proxy(settings["proxy"])
    if proxy and not proxy.is_valid(ALLOWED_PROXY_PROTOCOLS):
        _notify_invalid_proxy(ls, proxy)
        return False

    # Parse and clean code entity
    code_entity = get_entity_at_cursor(document.source, cursor)
    if not code_entity or not isinstance(code_entity, BaseFunction):
        _notify_invalid_context(ls)
        return False
    cleaned_code_entity = code_entity.clean_code()

    # Prepare the docstring generation prompt
    prompt = _prepare_docstring_prompt(settings, cleaned_code_entity)
    ls.log_to_output(f"Prompt used:\n{prompt}")

    # Create a future to track the progress cancellation
    progress = ls.progress.tokens.setdefault(progress_token, Future())

    # Start the progress reporting task
    report_task = asyncio.create_task(
        _report_progress(ls, progress_token, settings["requestTimeout"])
    )

    # Generate docstring
    docstring_task = asyncio.create_task(
        generate_docstring(
            api_key=api_key,
            base_url=settings["baseUrl"],
            model=settings["aiModel"],
            prompt=prompt,
            proxy=proxy,
        )
    )

    # Handle cancellations
    progress.add_done_callback(docstring_task.cancel)
    docstring_task.add_done_callback(report_task.cancel)

    # Await docstring generation
    try:
        docstring = await asyncio.wait_for(docstring_task, settings["requestTimeout"])
    except (asyncio.CancelledError, asyncio.TimeoutError):
        return False
    except Exception as err:
        raise err

    ls.log_to_output(f"Response received:\n{docstring}")

    # Define the position of the existing docstring
    existing_docstring_range = _get_docstring_range(code_entity)

    # Define the insertion position of the docstring
    docstring_insert_position = (
        lsp.Position(existing_docstring_range.start.line, 0)
        if existing_docstring_range
        else lsp.Position(code_entity.signature_end.line, 0)
    )

    # Extract, format and apply the docstring
    docstring = parse_docstring(docstring)
    docstring = format_docstring(
        docstring, code_entity.indent_level + 1, settings["onNewLine"]
    )
    docstring = match_line_endings(document, docstring)

    await _add_docstring_to_document(
        ls,
        docstring,
        docstring_insert_position,
        existing_docstring_range,
        document,
        document_version,
    )

    return True


def _unpack_args(
    args: tuple[TextDocumentPosition, str, lsp.ProgressToken]
) -> tuple[str, lsp.Position, str, lsp.ProgressToken]:
    """Unpacks the LSP command arguments."""
    args = CommandArguments(*args)
    uri = args.text_document_position["textDocument"]["uri"]
    cursor = lsp.Position(**args.text_document_position["position"])
    return uri, cursor, args.api_key, args.progress_token


def _create_proxy(proxy_settings: ProxySettings) -> Proxy | None:
    """Creates a Proxy instance from settings; returns None if no URL."""
    if not proxy_settings["url"]:
        return None
    return Proxy(
        url=proxy_settings["url"],
        authorization=proxy_settings["authorization"],
        strict_ssl=proxy_settings["strictSSL"],
    )


def _notify_invalid_proxy(ls: server.DocstringLanguageServer, proxy: Proxy) -> None:
    """Shows warning if the provided proxy URL is invalid."""
    ls.show_warning(
        (
            f"The proxy URL ({proxy.url}) is not valid. "
            "The format of the URL is: "
            "`<protocol>://[<username>:<password>@]<host>:<port>`. "
            f"Where `protocol` can be: {', '.join(ALLOWED_PROXY_PROTOCOLS)}. "
            "The username and password are optional. "
            "Examples: `http://proxy.com:80`, `http://127.0.0.1:80`, "
            "`socks5://user:password@127.0.0.1:1080`"
        )
    )


def _notify_invalid_context(ls: server.DocstringLanguageServer) -> None:
    """Shows warning if the code entity for generating docstring cannot be determined."""
    ls.show_warning(
        "Failed to determine the Python code entity for generating the docstring. "
        "The code may contain a syntax error. "
        "Make sure the cursor is positioned inside a function."
    )


def _prepare_docstring_prompt(settings: dict, code: str) -> str:
    """Prepares the prompt for docstring generation."""
    return settings["promptPattern"].format(
        docstring_style=settings["docstringStyle"], code=code
    )


async def _report_progress(
    ls: server.DocstringLanguageServer, progress_token: lsp.ProgressToken, timeout: int
) -> None:
    """Reports the progress of the docstring generation."""
    while timeout != 0:
        ls.progress.report(
            progress_token,
            lsp.WorkDoneProgressReport(
                message=f"Waiting for AI response ({timeout} secs)..."
            ),
        )
        await asyncio.sleep(1)
        timeout -= 1


def _get_docstring_range(code_entity: CodeEntity) -> lsp.Range | None:
    """Returns the adjusted range of a code entity docstring, or None if not present.

    This range is used to remove lines from the text document.
    """
    if not (doc_range := code_entity.docstring_range):
        return None
    return lsp.Range(
        lsp.Position(doc_range.start.line - 1, 0),
        lsp.Position(doc_range.end.line, 0),
    )


def _create_workspace_edit(
    document: LSPTextDocument,
    document_version: int,
    text_edits: list[lsp.TextEdit],
) -> lsp.WorkspaceEdit:
    """Creates a WorkspaceEdit with the specified text edits for the given document."""
    return lsp.WorkspaceEdit(
        document_changes=[
            lsp.TextDocumentEdit(
                text_document=lsp.OptionalVersionedTextDocumentIdentifier(
                    uri=document.uri,
                    version=document_version,
                ),
                edits=text_edits,  # type: ignore
            )
        ]
    )


async def _add_docstring_to_document(
    ls: server.DocstringLanguageServer,
    docstring: str,
    docstring_insert_position: lsp.Position,
    existing_docstring_range: lsp.Range | None,
    document: LSPTextDocument,
    document_version: int,
) -> None:
    """Adds the generated docstring to the document."""
    text_edits = []

    # Remove existing docstring if present
    if existing_docstring_range:
        text_edits.append(lsp.TextEdit(range=existing_docstring_range, new_text=""))

    # Insert new docstring
    text_edits.append(
        lsp.TextEdit(
            range=lsp.Range(docstring_insert_position, docstring_insert_position),
            new_text=docstring,
        )
    )

    workspace_edit = _create_workspace_edit(document, document_version, text_edits)
    result = await cast(
        Awaitable[lsp.ApplyWorkspaceEditResult], ls.apply_edit_async(workspace_edit)
    )

    if not result.applied:
        reason = (
            result.failure_reason
            or "maybe you made changes to the source code at generation time"
        )
        ls.show_warning(f"Failed to add docstring to source code ({reason})")
