import json
import os
import sys

import lsprotocol.types as lsp

import server
from settings import GlobalSettings, WorkspaceSettings
from utils import mark_as_feature


@mark_as_feature(lsp.INITIALIZE)
def initialize(
    ls: "server.DocstringLanguageServer", params: lsp.InitializeParams
) -> None:
    """LSP handler for initialize request."""
    ls.log_to_output(f"CWD Server: {os.getcwd()}")
    ls.log_to_output(f"PID Server: {os.getpid()}")

    paths = f"{os.linesep}   ".join(sys.path)
    ls.log_to_output(f"sys.path used to run Server:{os.linesep}   {paths}")

    initialization_options = params.initialization_options or {}

    global_settings = initialization_options.get("globalSettings", {})
    ls.global_settings = GlobalSettings(global_settings)

    workspace_settings = initialization_options.get("settings", {})
    ls.workspace_settings = WorkspaceSettings(workspace_settings, ls.global_settings)

    # fmt: off
    global_settings_output = json.dumps(
        ls.global_settings, indent=4, ensure_ascii=False
    )
    workspace_settings_output = json.dumps(
        ls.workspace_settings, indent=4, ensure_ascii=False
    )

    ls.log_to_output(
        f"Global settings:{os.linesep}{global_settings_output}{os.linesep}"
    )
    ls.log_to_output(
        f"Settings used to run Server:{os.linesep}{workspace_settings_output}{os.linesep}"
    )
    # fmt: on
