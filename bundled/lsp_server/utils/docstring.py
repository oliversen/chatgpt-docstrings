import re

import openai


async def get_docstring(api_key: str, model: str, prompt: str) -> str:
    openai.api_key = api_key
    response = await openai.ChatCompletion.acreate(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "When you generate a docstring, "
                    "return me only a string that I can add to my code."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    docstring = response.choices[0].message.content
    return docstring


def format_docstring(
    docstring: str, indent_level: int, docs_new_line: bool, quotes_new_line: bool
) -> str:
    # remove function source code including markdown tags
    if docstring.strip().startswith(("def ", "async ", "```")):
        match = re.search(r'""".*?"""', docstring, flags=re.DOTALL)
        docstring = match.group() if match else docstring
    # remove leading and trailing whitespaces, newlines, quotes
    docstring = docstring.strip().strip('"""').strip("\r\n")
    # remove indents
    if docstring.startswith("    "):
        lines = docstring.splitlines(True)
        docstring = "".join([re.sub(r"^\s{4}", "", line) for line in lines])
    # split docstring on lines
    docstring_lines = docstring.splitlines()
    # check docstring for multi-line
    if len(docstring_lines) > 1:
        # eol conversion to single format
        docstring = "\n".join(docstring_lines)
        # add new lines for docstring
        docstring = f"\n{docstring}\n" if docs_new_line else f"{docstring}\n"
    # add quotes
    docstring = f'"""{docstring}"""'
    # add indents
    indents = " " * indent_level * 4
    docstring = "".join([f"{indents}{line}" for line in docstring.splitlines(True)])
    # add new line for opening quotes
    docstring = f"\n{docstring}" if quotes_new_line else docstring
    return docstring
