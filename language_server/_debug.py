import os
import pathlib
import runpy
import sys

SERVER_START_SCRIPT_PATH = os.fspath(pathlib.Path(__file__).parent / "_start.py")

if debugger_path := os.getenv("DEBUGPY_PATH"):
    if debugger_path.endswith("debugpy"):
        debugger_path = os.fspath(pathlib.Path(debugger_path).parent)

    sys.path.append(debugger_path)
    import debugpy  # type: ignore

    # 5678 is the default port, If you need to change it update it here
    # and in launch.json.
    debugpy.connect(5678)
    # This will ensure that execution is paused as soon as the debugger
    # connects to VS Code.
    debugpy.breakpoint()


runpy.run_path(SERVER_START_SCRIPT_PATH, run_name="__main__")
