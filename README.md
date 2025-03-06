<p align="center">
    <img width="190" src="/images/icon.png" />
</p>
<h1 align="center">ChatGPT: Docstring Generator</h1>
<p align="center">
    <a src="https://marketplace.visualstudio.com/items?itemName=oliversen.chatgpt-docstrings"><img alt="" src="https://img.shields.io/visual-studio-marketplace/v/oliversen.chatgpt-docstrings?style=for-the-badge&color=00b3a1&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgdmlld0JveD0iMCAwIDMyIDMyIj4KCTxwYXRoIGZpbGw9IiNlZGY4ZmYiIGQ9Im0xMS43MiAxOC42ODVsLTYuODgzIDUuMTg0TDIgMjIuOTIyTDkgMTZMMiA5LjA3N2wyLjgzNy0uOTQ3bDYuODgzIDUuMTg0bDExLjQzMy0xMS4zTDMwIDQuOTIydjIyLjE1NWwtNi44NDcgMi45MDlaTTE1LjI4NyAxNmw3Ljg2NSA1LjkyM1YxMC4wNzZaIiAvPgo8L3N2Zz4="></a>
    <img alt="GitHub" src="https://img.shields.io/github/license/oliversen/chatgpt-docstrings?style=for-the-badge&color=00b3a1&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGZpbGw9IiNmZmZmZmYiIHdpZHRoPSI4MDBweCIgaGVpZ2h0PSI4MDBweCIgdmlld0JveD0iMCAwIDE0IDE0IiByb2xlPSJpbWciIGZvY3VzYWJsZT0iZmFsc2UiIGFyaWEtaGlkZGVuPSJ0cnVlIj48cGF0aCBkPSJNIDYuOTk5OTgxNiwxIEMgMy42ODYyODMsMSAxLDMuNzc0NDggMSw3LjE5NzAyIDEsOS44NTM1NCAyLjYxODg5NywxMi4xMTg4NSA0Ljg5MzA1ODksMTMgTCA2LjI3NTcyNzksOS4xOTE3OSBDIDUuNDk0MDAxNSw4Ljg4ODk0IDQuOTM3NDkzOSw4LjExMDE5IDQuOTM3NDkzOSw3LjE5NzAyIGMgMCwtMS4xNzY0OSAwLjkyMzQzMzMsLTIuMTMwMjQgMi4wNjI0ODc3LC0yLjEzMDI0IDEuMTM5MDkxMSwwIDIuMDYyNTYwNSwwLjk1Mzc1IDIuMDYyNTYwNSwyLjEzMDI0IDAsMC45MTMxNyAtMC41NTY1NDUsMS42OTE5MiAtMS4zMzgyNzA1LDEuOTk0NzcgTCA5LjEwNjk0MDcsMTMgQyAxMS4zODEwNjYsMTIuMTE4ODUgMTMsOS44NTM1NCAxMyw3LjE5NzAyIDEzLDMuNzc0NDggMTAuMzEzNzU0LDEgNi45OTk5ODE2LDEgWiIgZmlsbD0iI2ZmZmZmZiIvPjwvc3ZnPg%3D%3D">
</p>
<p align="center"><b>Automatically generate Python docstrings using ChatGPT.</b></p>

![Demo](/images/readme/demo.gif)

> Notice!
>
> - To use the extension, **you need an [API key](#api-key)** from [OpenAI](https://platform.openai.com/account/api-keys) or [another OpenAI-compatible provider](#switching-ai-providers).
> - **This is a pre-release** version of the extension. In case of issues, please keep [feedback](https://github.com/oliversen/chatgpt-docstrings/issues) on github.

## Table of Contents

- [Installation](#installation)
- [Requirements](#requirements)
- [Usage](#usage)
  - [Code Completion](#code-completion)
  - [Context Menu](#context-menu)
  - [Command Palette](#command-palette)
  - [Keyboard Shortcut](#keyboard-shortcut)
- [API key](#api-key)
- [Switching AI Providers](#switching-ai-providers)
- [Settings](#settings)
- [Telemetry](#telemetry)
- [Change Log](#change-log)
- [Feedback](#feedback)
- [Contribution](#contribution)
- [License](#license)

---

## Installation

Install it from [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=oliversen.chatgpt-docstrings) or download and install .vsix file from [Releases](https://github.com/oliversen/chatgpt-docstrings/releases).

---

## Requirements

- VSCode 1.78.0 or greater
- Python 3.9 or greater

---

## Usage

### Code Completion

Type `"""` and select `Generate Docstring (ChatGPT)` from the completion items.

![Code Completion](/images/readme/code_completion.png)

### Context Menu

Right click in the Text Editor area and select `Generate Docstring (ChatGPT)`.

![Context Menu](/images/readme/context_menu.png)

### Command Palette

Open the Command Palette (F1), type `docstring` and select `Generate Docstring (ChatGPT)`.

![Command Palette](/images/readme/command_palette.png)

### Keyboard Shortcut

Use the following keyboard shortcut:

- Windows/Linux: `Ctrl+Alt+D`
- Mac: `Cmd+Opt+D`

![Keyboard Shortcut](/images/readme/keyboard_shortcut.png)

> You can change the default keyboard shortcut by Keyboard Shortcuts editor ***(File > Preferences > Keyboard Shortcuts***).

---

## API key

To use the extension, you need an API key from [OpenAI](https://platform.openai.com/account/api-keys) or [another OpenAI-compatible provider](#switching-ai-providers).

### How to Set or Change API Key

When you first generate a docstring, a pop-up window will appear requesting you to enter your API key. You can change the API key through the Settings editor (***File > Preferences > Settings > Extensions > ChatGPT: Docstring Generator***). Or using the `Set API key` command in the Command Palette (F1).

---

## Switching AI Providers

By default, this extension uses OpenAI API to generate docstrings. However, you can easily switch to other AI services that support OpenAI-compatible APIs.

### How to Change AI Provider

1. **Set the Base URL:** In the extension settings, locate the `baseUrl` parameter. You can change this to point to a different OpenAI-compatible API, such as [OpenRouter](https://openrouter.ai), which offers access to a variety of AI models. For example, to use [OpenRouter](https://openrouter.ai), set the `baseUrl` to: `https://openrouter.ai/api/v1`
2. **Specify the AI Model:** To specify which model you want to use, locate the `aiModelCustom` parameter in the settings. Here, you can define the exact AI model you wish to interact with, depending on the service you're using. For example, if you're using [OpenRouter](https://openrouter.ai), you might choose from models such as `anthropic/claude-3.5-haiku`, `google/gemini-pro-1.5`, or others depending on availability.
3. **Set the API Key:** [Set your API key](#how-to-set-or-change-api-key) for the selected AI service. You can obtain this key from the service website.

Now, the extension will route requests through the selected AI service. Ensure the provider you choose is compatible with OpenAI’s API.

---

## Settings

- `chatgpt-docstrings.interpreter`: Path to the Python executable used to start the language server. If not set, the Python interpreter selected in the VSCode status bar is used.

  - *Default value*: []

- `chatgpt-docstrings.baseUrl`: The base URL for the OpenAI-compatible API.

  - *Default value*: "`https://api.openai.com/v1`"

- `chatgpt-docstrings.aiModel`: Which AI language model to use. GPT-4, GPT-4 Turbo, and GPT-4o are available in the OpenAI API to paying customers.

  - *Default value*: "gpt-4o-mini"
  - *Available options*:
    - "gpt-4o-mini"
    - "gpt-4o"
    - "gpt-4-turbo"
    - "gpt-4"
    - "gpt-3.5-turbo"

- `chatgpt-docstrings.aiModelCustom`: If set, overrides the model configured in `chatgpt-docstrings.aiModel`.

  - *Default value*: ""

- `chatgpt-docstrings.docstringStyle`: Which the docstring style to use.

  - *Default value*: "google"
  - *Available options*:
    - "google"
    - "numpy"
    - "sphinx"

- `chatgpt-docstrings.onNewLine`: Option to start the docstring on a new line after the triple quotes.

  - *Default value*: false
  - *Available options*:
    - true
    - false

  > This option is ignored when generating one-line docstrings.

- `chatgpt-docstrings.promptPattern`: The AI prompt used to generate docstrings.

  - *Default value*: "Generate a {docstring_style}-style docstring for the following Python {entity} code:\n{code}"

  > Placeholders enclosed in curly brackets `{}` will be replaced as follows:
  > - `{docstring_style}` — the value of the parameter `chatgpt-docstrings.docstringStyle`
  > - `{entity}` — the type of code entity, such as "function" or "class", based on the context
  > - `{code}` — the source code of the function or class for which the docstring will be generated
  >
  > **Example**: Generate a google-style docstring for the following Python function code:\n def sum(x, y): ...

- `chatgpt-docstrings.requestTimeout`: The timeout in seconds to use when sending AI API requests.

  - *Default value*: 15

- `chatgpt-docstrings.showProgressNotification`: Option to display a notification about the progress of docstring generation.

  - *Default value*: true
  - *Available options*:
    - true
    - false

- `chatgpt-docstrings.codeAnalyzer`: Which Python library to use for analyzing source files. Jedi is a third-party package. Jedi may not support the latest versions of Python. `ast` is a module of the Python Standard Library. With `ast`, syntax errors in the code are not allowed.

  - *Default value*: "jedi"
  - *Available options*:
    - "jedi"
    - "ast"

- `chatgpt-docstrings.proxy`: The URL of the proxy server for AI API requests. The format of the URL is: `<protocol>://[<username>:<password>@]<host>:<port>`. Where `protocol` can be: 'http', 'https', 'socks5' or 'socks5h'. The username and password are optional. If not set, will be inherited from the `http.proxy` setting.

  - *Default value*: ""
  - *Examples*:
    - `http://proxy.com:80`
    - `http://127.0.0.1:80`
    - `socks5://user:password@127.0.0.1:1080`

- `chatgpt-docstrings.proxyAuthorization`: The value to send as the `Proxy-Authorization` HTTP header.

  - *Default value*: ""

- `chatgpt-docstrings.proxyStrictSSL`: "Controls whether the proxy server certificate should be verified against the list of supplied CAs."

  - *Default value*: false
  - *Available options*:
    - true
    - false

---

## Telemetry

This extension collects anonymous information related to the usage of the extension, such as well as performance and error data. You can disable telemetry as described [here](https://code.visualstudio.com/docs/getstarted/telemetry#_disable-telemetry-reporting).

---

## Change Log

See Change Log [here](CHANGELOG.md)

---

## Feedback

Submit the [issues](https://github.com/oliversen/chatgpt-docstrings/issues) if you find any bug or have any suggestion.

---

## Contribution

Fork the [repo](https://github.com/oliversen/chatgpt-docstrings) and submit pull requests.

---

## License

This extension is licensed under the [MIT License](LICENSE)
