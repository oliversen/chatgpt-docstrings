from __future__ import annotations

from pytest import mark

from language_server.utils.docstring import parse_docstring

PLAIN = """
Add two integers.

Args:
    x: The first integer.
    y: The second integer.

Returns:
    The sum of x and y.
"""


WITH_QUOTES = '''
"""Add two integers.

Args:
    x: The first integer.
    y: The second integer.

Returns:
    The sum of x and y.
"""
'''


WITH_QUOTES_AND_INDENTATION = '''
"""
    Add two integers.

    Args:
        x: The first integer.
        y: The second integer.

    Returns:
        The sum of x and y.
"""
'''


WITH_BACKTICKS = """
```
    Add two integers.

    Args:
        x: The first integer.
        y: The second integer.

    Returns:
        The sum of x and y.
```
"""


WITH_INDENTED_BACKTICKS = """
    ```
    Add two integers.

    Args:
        x: The first integer.
        y: The second integer.

    Returns:
        The sum of x and y.
    ```
"""


WITH_BLANK_LINES = (
    "    \n"
    "\n"
    "    \n"
    "    Add two integers.\n"
    "\n"
    "    Args:\n"
    "        x: The first integer.\n"
    "        y: The second integer.\n"
    "\n"
    "    Returns:\n"
    "        The sum of x and y.  \n"
    "    \n"
    "\n"
    "    "
)


WITH_CODE = '''
def sum(x, y):
    """
        Add two integers.

        Args:
            x: The first integer.
            y: The second integer.

        Returns:
            The sum of x and y.
    """
    return x + y
'''


WITH_MARKDOWN = '''
```python
def sum(x, y):
    """
        Add two integers.

        Args:
            x: The first integer.
            y: The second integer.

        Returns:
            The sum of x and y.
    """
    return x + y
```
'''


DOCSTRINGS = (
    PLAIN,
    WITH_QUOTES,
    WITH_QUOTES_AND_INDENTATION,
    WITH_BACKTICKS,
    WITH_INDENTED_BACKTICKS,
    WITH_BLANK_LINES,
    WITH_CODE,
    WITH_MARKDOWN,
)


@mark.parametrize("docstring", DOCSTRINGS)
def test_multiline_docstring(docstring: str) -> None:
    expected = (
        "Add two integers.\n"
        "\n"
        "Args:\n"
        "    x: The first integer.\n"
        "    y: The second integer.\n"
        "\n"
        "Returns:\n"
        "    The sum of x and y."
    )
    assert parse_docstring(docstring) == expected
