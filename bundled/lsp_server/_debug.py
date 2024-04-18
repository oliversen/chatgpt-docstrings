"""Debugging support for LSP."""

import os
import pathlib
import runpy
import sys


# Ensure debugger is loaded before we load anything else, to debug initialization.
debugger_path = os.getenv("DEBUGPY_PATH", None)
if debugger_path:
    if debugger_path.endswith("debugpy"):
        debugger_path = os.fspath(pathlib.Path(debugger_path).parent)

    # Update sys.path before importing any bundled libraries.
    sys.path.insert(0, debugger_path)

    import debugpy

    # 5678 is the default port, If you need to change it update it here
    # and in launch.json.
    debugpy.connect(5678)

    # This will ensure that execution is paused as soon as the debugger
    # connects to VS Code. If you don't want to pause here comment this
    # line and set breakpoints as appropriate.
    debugpy.breakpoint()

SERVER_PATH = os.fspath(pathlib.Path(__file__).parent / "_start.py")
# NOTE: Set breakpoint in `lsp_server.py` before continuing.
runpy.run_path(SERVER_PATH, run_name="__main__")
