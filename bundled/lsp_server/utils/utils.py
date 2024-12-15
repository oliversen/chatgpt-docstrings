from __future__ import annotations

import httpx
import lsprotocol.types as lsp
from openai import DefaultAsyncHttpxClient
from pygls import workspace

from .proxy import Proxy


def create_workspace_edit(
    document: lsp.Document, document_version: int, text_edits: list[lsp.TextEdit]
) -> lsp.WorkspaceEdit:
    """Creates a WorkspaceEdit with the specified text edits for the given document."""
    return lsp.WorkspaceEdit(
        document_changes=[
            lsp.TextDocumentEdit(
                text_document=lsp.VersionedTextDocumentIdentifier(
                    uri=document.uri,
                    version=document_version,
                ),
                edits=text_edits,
            )
        ]
    )


def get_line_endings(lines: list[str]) -> str:
    """Returns line endings used in the text."""
    try:
        if lines[0][-2:] == "\r\n":
            return "\r\n"
        return "\n"
    except Exception:
        return None


def match_line_endings(document: workspace.Document, text: str) -> str:
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
