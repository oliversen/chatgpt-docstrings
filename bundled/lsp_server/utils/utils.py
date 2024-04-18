from __future__ import annotations

import lsprotocol.types as lsp
from pygls import workspace


def create_workspace_edit(
    document: lsp.Document, text_edits: list[lsp.TextEdit]
) -> lsp.WorkspaceEdit:
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
