import json
import os
import sys

import lsprotocol.types as lsp

from log import log_to_output
from server import LSP_SERVER
from settings import GLOBAL_SETTINGS, WORKSPACE_SETTINGS


@LSP_SERVER.feature(lsp.INITIALIZE)
def initialize(params: lsp.InitializeParams) -> None:
    """LSP handler for initialize request."""
    log_to_output(f"CWD Server: {os.getcwd()}")
    log_to_output(f"PID Server: {os.getpid()}")

    paths = "{os.linesep}   ".join(sys.path)
    log_to_output(f"sys.path used to run Server:{os.linesep}   {paths}")

    GLOBAL_SETTINGS.initialize(params.initialization_options.get("globalSettings", {}))
    WORKSPACE_SETTINGS.initialize(params.initialization_options.get("settings", {}))

    # fmt: off
    global_settings_output = json.dumps(
        GLOBAL_SETTINGS, indent=4, ensure_ascii=False
    )
    workspace_settings_output = json.dumps(
        WORKSPACE_SETTINGS, indent=4, ensure_ascii=False
    )

    log_to_output(
        f"Global settings:{os.linesep}{global_settings_output}{os.linesep}"
    )
    log_to_output(
        f"Settings used to run Server:{os.linesep}{workspace_settings_output}{os.linesep}"
    )
