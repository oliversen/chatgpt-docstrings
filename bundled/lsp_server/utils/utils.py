from __future__ import annotations

from functools import partial

import aiohttp
import lsprotocol.types as lsp
from aiohttp_socks import ProxyConnector
from pygls import workspace

from .proxy import Proxy


def create_workspace_edit(
    document: lsp.Document, text_edits: list[lsp.TextEdit]
) -> lsp.WorkspaceEdit:
    """Creates a WorkspaceEdit with the specified text edits for the given document."""
    return lsp.WorkspaceEdit(
        document_changes=[
            lsp.TextDocumentEdit(
                text_document=lsp.VersionedTextDocumentIdentifier(
                    uri=document.uri,
                    version=0 if document.version is None else document.version,
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


def create_aiosession(proxy: Proxy | None) -> aiohttp.ClientSession:
    """Creates aiohttp.ClientSession based on the proxy settings."""
    if proxy:
        proxy_url = proxy.url.replace("https://", "http://")
        if proxy_url.startswith("http://"):
            headers = {"Proxy-Authorization": proxy.authorization}
            session = aiohttp.ClientSession(proxy=proxy_url, headers=headers)
            session.request = partial(session.request, ssl=proxy.strict_ssl)
        else:
            connector = ProxyConnector.from_url(proxy_url, ssl=proxy.strict_ssl)
            session = aiohttp.ClientSession(connector=connector)
    else:
        session = aiohttp.ClientSession(trust_env=True)
    return session
