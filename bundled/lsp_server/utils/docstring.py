from __future__ import annotations

import re

from openai import AsyncOpenAI, OpenAIError

from . import create_httpx_client
from .proxy import Proxy


async def get_docstring(
    api_key: str, model: str, prompt: str, proxy: Proxy | None = None
) -> str | None:
    """Generates a docstring using the OpenAI API."""
    client = AsyncOpenAI(
        api_key=api_key,
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

    if response.choices is not None:
        docstring = response.choices[0].message.content
        return docstring
    elif hasattr(response, "error"):
        raise OpenAIError(response.error["message"])
    else:
        raise OpenAIError("Invalid response from API.")


def format_docstring(
    docstring: str, indent_level: int, docs_new_line: bool, quotes_new_line: bool
) -> str:
    """Formats a given docstring by cleaning, adjusting indentation, and adding quotes."""
    # Extract docstring if it starts with specific function or code block syntax
    if docstring.strip().startswith(("def ", "async ", "```")):
        match = re.search(r'""".*?"""', docstring, flags=re.DOTALL)
        docstring = match.group() if match else docstring

    # Clean up the docstring, removing any leading/trailing triple quotes and newlines
    docstring = docstring.strip().strip('"""').strip("\r\n")

    # Remove leading indentation if it exists (i.e., remove the first 4 spaces)
    if docstring.startswith("    "):
        lines = docstring.splitlines(True)
        docstring = "".join([re.sub(r"^\s{4}", "", line) for line in lines])

    # Split docstring into lines and adjust based on 'docs_new_line'
    docstring_lines = docstring.splitlines()
    if len(docstring_lines) > 1:
        docstring = "\n".join(docstring_lines)
        docstring = f"\n{docstring}\n" if docs_new_line else f"{docstring}\n"

    # Add triple quotes around the docstring
    docstring = f'"""{docstring}"""'

    # Apply indentation to each line in the docstring
    indents = " " * indent_level * 4
    docstring = "".join([f"{indents}{line}" for line in docstring.splitlines(True)])

    # Optionally add a newline before the quotes
    if quotes_new_line:
        docstring = f"\n{docstring}"

    return docstring
