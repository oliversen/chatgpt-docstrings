# ChatGPT: Docstrings Generator

[![Visual Studio Marketplace Version](https://img.shields.io/visual-studio-marketplace/v/oliversen.chatgpt-docstrings?style=flat-square)](https://marketplace.visualstudio.com/items?itemName=oliversen.chatgpt-docstrings) [![Visual Studio Marketplace Installs](https://img.shields.io/visual-studio-marketplace/i/oliversen.chatgpt-docstrings?style=flat-square)](https://marketplace.visualstudio.com/items?itemName=oliversen.chatgpt-docstrings) [![Visual Studio Marketplace Downloads](https://img.shields.io/visual-studio-marketplace/d/oliversen.chatgpt-docstrings?style=flat-square)](https://marketplace.visualstudio.com/items?itemName=oliversen.chatgpt-docstrings) [![Visual Studio Marketplace Rating (Stars)](https://img.shields.io/visual-studio-marketplace/stars/oliversen.chatgpt-docstrings?style=flat-square)](https://marketplace.visualstudio.com/items?itemName=oliversen.chatgpt-docstrings) [![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](LICENSE)

Automatically generate docstrings using ChatGPT.

![Demo](/images/demo.gif)

## Installation

Install it from [Visual Studio Marketplace](https://marketplace.visualstudio.com) or download and install .vsix file from [Releases](https://github.com/oliversen/chatgpt-docstrings/releases).

**After installation, you need to set your OpenAI API key in the extension settings (File > Preferences > Settings > Extensions > ChatGPT: Docstrings Generator > Openai Api Key). You can get the key [here](https://platform.openai.com/account/api-keys).**

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

## Settings

- `chatgpt-docstrings.interpreter`: When set to a path to python executable, extension will use that to launch the server and any subprocess.

  - *Default value*: []

- `chatgpt-docstrings.openaiApiKey`: The extension needs to be configured with your account's secret key which is available on the [website](https://platform.openai.com/account/api-keys).

  - *Default value*: ""

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
