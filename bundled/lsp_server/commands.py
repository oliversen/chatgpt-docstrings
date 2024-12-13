from __future__ import annotations

import asyncio

import lsprotocol.types as lsp
import pygls

from log import log_to_output
from notification import show_info, show_warning
from server import LSP_SERVER
from settings import WORKSPACE_SETTINGS
from utils import create_workspace_edit, match_line_endings
from utils.code_cleaner import FuncCleaner
from utils.code_parser import FuncParser, NotFuncException
from utils.docstring import format_docstring, get_docstring
from utils.proxy import Proxy, is_valid_proxy


@LSP_SERVER.command("chatgpt-docstrings.applyGenerate")
async def apply_generate_docstring(
    ls: pygls.server.LanguageServer,
    args: list[lsp.TextDocumentPositionParams, str, str],
) -> None:
    uri = args[0]["textDocument"]["uri"]
    openai_api_key = args[1]
    progress_token = args[2]
    document = ls.workspace.get_document(uri)
    document_version = document.version or 0
    source = document.source
    # TODO: edit cursor
    cursor = lsp.Position(**args[0]["position"])
    settings = WORKSPACE_SETTINGS.by_document(document)
    openai_model = settings["openaiModel"]
    prompt_pattern = settings["promptPattern"]
    docstring_style = settings["docstringStyle"]
    docs_new_line = settings["onNewLine"]
    response_timeout = settings["responseTimeout"]
    proxy = settings["proxy"].copy()
    proxy["strict_ssl"] = proxy.pop("strictSSL")
    proxy = Proxy(**proxy) if proxy["url"] else None

    # proxy validation
    if proxy and not is_valid_proxy(proxy.url):
        show_warning(
            (
                f"The proxy URL ({proxy.url}) is not valid. "
                "The format of the URL is: "
                "`<protocol>://[<username>:<password>@]<host>:<port>`. "
                "Where `protocol` can be: `http`, `https`, `socks4` or `socks5`. "
                "The username and password are optional. "
                "Examples: `http://proxy.com:80`, `http://127.0.0.1:80`, "
                "`socks5://user:password@127.0.0.1:1080`"
            )
        )
        return

    # get function source
    try:
        parsed_func = FuncParser(source, cursor)
    except NotFuncException:
        show_info("The cursor must be set inside the function.")
        return

    # clean function
    func_cleaner = FuncCleaner(parsed_func)
    cleaned_func = func_cleaner.clean(indents=True, docstring=True, blank_lines=True)

    # format prompt
    prompt = prompt_pattern.format(
        docstring_style=docstring_style, function=cleaned_func
    )
    log_to_output(f"Prompt used:\n{prompt}")

    # get gocstring
    with ls.progress(progress_token) as progress:
        task = asyncio.create_task(
            get_docstring(openai_api_key, openai_model, prompt, proxy)
        )
        while 1:
            if task.done():
                break
            if response_timeout == 0:
                task.cancel()
                show_warning("ChatGPT response timed out.")
                return
            if progress.cancelled:
                task.cancel()
                return
            progress.report(
                f"Waiting for ChatGPT response ({response_timeout} secs)..."
            )
            await asyncio.sleep(1)
            response_timeout -= 1
        if task.exception():
            raise task.exception()
        docstring = task.result()
    log_to_output(f"Received ChatGPT docstring:\n{docstring}")

    # define docsting position
    if parsed_func.docstring_range:
        docstring_range = parsed_func.docstring_range
        docstring_range.start.character = 0
        quotes_new_line = False
    else:
        docstring_range = lsp.Range(parsed_func.suite, parsed_func.suite)
        quotes_new_line = True
    docstring_range.start.line -= 1
    docstring_range.end.line -= 1

    # format docstring
    docstring = format_docstring(
        docstring, parsed_func.indent_level + 1, docs_new_line, quotes_new_line
    )
    # TODO: remove it
    docstring = match_line_endings(document, docstring)

    # apply docstring
    text_edits = [lsp.TextEdit(range=docstring_range, new_text=docstring)]
    workspace_edit = create_workspace_edit(document, document_version, text_edits)
    result = await ls.apply_edit_async(workspace_edit)
    if not result.applied:
        reason = (
            result.failure_reason
            or "maybe you make changes to source code at generation time"
        )
        show_warning(f"Failed to add docstring to source code ({reason})")
        ls.send_telemetry_error("applyEditWorkspaceFail", {"reason": reason})
