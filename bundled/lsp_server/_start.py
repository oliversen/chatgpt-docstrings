import os
import sys
from pathlib import Path

# Update sys.path before importing any bundled libraries.
sys.path.insert(0, os.fspath(Path(__file__).parent.parent / "libs"))

from server import LSP_SERVER  # noqa

# register LSP features and commands
import initialize  # noqa
import shutdown  # noqa
import completions  # noqa
import commands  # noqa


LSP_SERVER.start_io()
