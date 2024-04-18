from __future__ import annotations

import re

import lsprotocol.types as lsp

from server import LSP_SERVER
from utils.code_parser import FuncParser, NotFuncException


@LSP_SERVER.feature(
    lsp.TEXT_DOCUMENT_COMPLETION, lsp.CompletionOptions(trigger_characters=['"'])
)
def completions(params: lsp.CompletionParams) -> None | lsp.CompletionList:
    """Returns completion items."""
    cursor = params.position
    uri = params.text_document.uri
    document = LSP_SERVER.workspace.get_document(uri)
    source = document.source

    validate = document.lines[cursor.line][0 : cursor.character]
    if re.match(r'^(\s{4})+"""$', validate):
        try:
            parsed_func = FuncParser(source, cursor)
        except NotFuncException:
            return
        if cursor.line != parsed_func.suite.line:
            return
        completion_text = (
            "" if parsed_func.docstring_range else 'Await docstring generation..."""'
        )
        return _create_completion_list(cursor, completion_text)
    return


def _create_completion_list(
    cursor: lsp.Position, completion_text: str
) -> lsp.CompletionList:
    return lsp.CompletionList(
        is_incomplete=False,
        items=[
            lsp.CompletionItem(
                label="Generate Docstring (ChatGPT)",
                kind=lsp.CompletionItemKind.Text,
                text_edit=lsp.TextEdit(
                    range=lsp.Range(start=cursor, end=cursor),
                    new_text=completion_text,
                ),
                command=lsp.Command(
                    title="Generate Docstring (ChatGPT)",
                    command="chatgpt-docstrings.generateDocstring",
                ),
            ),
        ],
    )
