<p align="center">
    <img width="190" src="/images/icon.png" />
</p>
<h1 align="center">ChatGPT: Docstring Generator</h1>
<p align="center">
    <a src="https://marketplace.visualstudio.com/items?itemName=oliversen.chatgpt-docstrings&ssr=false#overview"><img alt="Visual Studio Marketplace Version" src="https://img.shields.io/visual-studio-marketplace/v/oliversen.chatgpt-docstrings?style=for-the-badge&color=00b3a1&logo=visual-studio-code"></a>
    <img alt="GitHub" src="https://img.shields.io/github/license/oliversen/chatgpt-docstrings?style=for-the-badge&color=00b3a1&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGZpbGw9IiNmZmZmZmYiIHdpZHRoPSI4MDBweCIgaGVpZ2h0PSI4MDBweCIgdmlld0JveD0iMCAwIDE0IDE0IiByb2xlPSJpbWciIGZvY3VzYWJsZT0iZmFsc2UiIGFyaWEtaGlkZGVuPSJ0cnVlIj48cGF0aCBkPSJNIDYuOTk5OTgxNiwxIEMgMy42ODYyODMsMSAxLDMuNzc0NDggMSw3LjE5NzAyIDEsOS44NTM1NCAyLjYxODg5NywxMi4xMTg4NSA0Ljg5MzA1ODksMTMgTCA2LjI3NTcyNzksOS4xOTE3OSBDIDUuNDk0MDAxNSw4Ljg4ODk0IDQuOTM3NDkzOSw4LjExMDE5IDQuOTM3NDkzOSw3LjE5NzAyIGMgMCwtMS4xNzY0OSAwLjkyMzQzMzMsLTIuMTMwMjQgMi4wNjI0ODc3LC0yLjEzMDI0IDEuMTM5MDkxMSwwIDIuMDYyNTYwNSwwLjk1Mzc1IDIuMDYyNTYwNSwyLjEzMDI0IDAsMC45MTMxNyAtMC41NTY1NDUsMS42OTE5MiAtMS4zMzgyNzA1LDEuOTk0NzcgTCA5LjEwNjk0MDcsMTMgQyAxMS4zODEwNjYsMTIuMTE4ODUgMTMsOS44NTM1NCAxMyw3LjE5NzAyIDEzLDMuNzc0NDggMTAuMzEzNzU0LDEgNi45OTk5ODE2LDEgWiIgZmlsbD0iI2ZmZmZmZiIvPjwvc3ZnPg%3D%3D">
</p>
<p align="center"><b>Automatically generate docstrings using ChatGPT.</b></p>

![Demo](/images/demo.gif)

## Installation

Install it from [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=oliversen.chatgpt-docstrings) or download and install .vsix file from [Releases](https://github.com/oliversen/chatgpt-docstrings/releases).

## Requirements

- VSCode 1.75.0 or greater
- Python 3.7 or greater

## Usage

Set the cursor position inside the function for which you want to generate a docstring and generate it using one of the following methods:

### Command

Open the Command Palette (F1) and type “Generate Docstring”.

### Context Menu

Right click in the Text Editor area and choose “Generate Docstring”.

### Keyboard Shortcut

Use the following keyboard shortcut:

- Windows/Linux: `Ctrl+K Ctrl+D`
- Mac: `Cmd+K Cmd+D`

> You can change the default keyboard shortcut by Keyboard Shortcuts editor ***(File > Preferences > Keyboard Shortcuts***).

## OpenAI API key

To use the extension, you will need an OpenAI API key. To obtain one, follow these steps:

1. Go to OpenAI's [website](https://platform.openai.com/account/api-keys). Log in or sign up there.
2. Click on the Create new secret key button.
3. Copy the key and paste it into the field that will show up when you run the docstring generation.

> You can change the API key using the `Set OpenAI API key` command in the Command Palette (F1).

## Settings

- `chatgpt-docstrings.interpreter`: When set to a path to python executable, extension will use that to launch the server and any subprocess.

  - *Default value*: []

- `chatgpt-docstrings.openaiModel`: Which OpenAI model to use.

  - *Default value*: "gpt-3.5-turbo"
  - *Available options*:
    - "gpt-3.5-turbo"
    - "text-davinci-002"

  > According to personal observations, "gpt-3.5-turbo" makes generation more correct, and "text-davinci-002" is faster.

- `chatgpt-docstrings.docstringFormat`: Which docstring format to use.

  - *Default value*: "google"
  - *Available options*:
    - "google"
    - "numpy"
    - "sphinx"

- `chatgpt-docstrings.chatgptPromptPattern`: The prompt to generate docstring.

  - *Default value*: "Create docstring in {docstring_format} format for python function below:\n{function}"

  > The expression `{docstring_format}` used in the prompt will be replaced with the value of the parameter `chatgpt-docstrings.docstringFormat`, `{function}` — with the source code of the function for which the docstring will be generated.

## Change Log

See Change Log [here](CHANGELOG.md)

## Feedback

Submit the [issues](https://github.com/oliversen/chatgpt-docstrings/issues) if you find any bug or have any suggestion.

## Contribution

Fork the [repo](https://github.com/oliversen/chatgpt-docstrings) and submit pull requests.

## License

This extension is licensed under the [MIT License](LICENSE)
