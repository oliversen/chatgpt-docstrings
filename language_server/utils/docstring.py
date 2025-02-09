from __future__ import annotations

import re

from openai import AsyncOpenAI, OpenAIError

from . import create_httpx_client, stub_for_tests
from .proxy import Proxy


@stub_for_tests(return_value='"""docstring"""')
async def generate_docstring(
    *,
    api_key: str,
    model: str,
    prompt: str,
    base_url: str | None = None,
    proxy: Proxy | None = None,
) -> str:
    """Generates a docstring using the OpenAI API."""
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,
        http_client=create_httpx_client(proxy),
    )

    system_message = (
        "When you generate a docstring, just give me the string without the code."
    )
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt},
    ]

    response = await client.chat.completions.create(
        model=model,
        messages=messages,  # type: ignore
        temperature=0,
    )

    if response.choices and (docstring := response.choices[0].message.content):
        return docstring
    elif error := getattr(response, "error", None):
        raise OpenAIError(error["message"])
    else:
        raise OpenAIError("Invalid response from API.")


def parse_docstring(docstring: str) -> str:
    """Extract and clean a docstring by removing quotes, blank lines, and indentation."""
    # Extract docstring from triple quotes
    match = re.search('"""(.+?)"""', docstring, re.DOTALL)
    docstring = match.group(1) if match else docstring

    # Remove leading/trailing quotes and blank lines
    # `.strip()` is not used to avoid losing indentation
    docstring = re.sub(r"^([\s`'\"]*[\r\n]+)+|[\s`'\"]*$", "", docstring)

    # Remove indentation
    lines = docstring.splitlines(True)
    indent = len(lines[0]) - len(lines[0].lstrip(" "))
    if indent:
        lines = [
            line[indent:] if line.startswith(" " * indent) else line for line in lines
        ]
        docstring = "".join(lines)

    return docstring


def format_docstring(docstring: str, indent_level: int, on_new_line: bool) -> str:
    """Formats a docstring with indentation, optional newlines, and triple quotes."""
    # Add newlines to the multiline docstring
    docstring_lines = docstring.splitlines()
    if len(docstring_lines) > 1:
        docstring = "\n".join(docstring_lines)
        docstring = f"\n{docstring}\n" if on_new_line else f"{docstring}\n"

    # Add triple quotes around the docstring
    docstring = f'"""{docstring}"""'

    # Add indentation
    indents = " " * indent_level * 4
    docstring = "".join([f"{indents}{line}" for line in docstring.splitlines(True)])

    # Add newline after the docstring
    docstring = f"{docstring}\n"

    return docstring
