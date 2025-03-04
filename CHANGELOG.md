# Changelog

All notable changes to this project will be documented in this file.

## [0.10.1] - 2025-01-17

### ⚙️ Other

- Improve formatting of generated docstring

## [0.10.0] - 2024-12-25

### 🚀 Features

- Add link to set API key in extension settings
- Add `aiModelCustom` option
- Add `baseUrl` option

### ⚙️ Other

- Change name of `openaiModel` option to `aiModel`
- Change name of `setOpenaiApiKey` command to `setApiKey`
- Change name of `responseTimeout` option to `requestTimeout`
- Add info about support for different AI providers

## [0.9.2] - 2024-12-17

### ⚙️ Other

- Сhange system message in OpenAI API request
- *(deps)* Remove deprecated python package `packaging`
- *(deps)* Bump python package `pygls` from 1.0.2 to 1.3.1
- *(deps)* Bump python package `openai` from 0.27.8 to 1.58.0

## [0.9.1] - 2024-12-12

### 🐛 Bug Fixes

- `Proxy-Authorisation` header for HTTP proxy is not used

### ⚙️ Other

- *(deps)* Bump python package `aiohttp` to 3.11.10
- *(deps)* Bump python package `aiohttp-socks` to 0.9.1

## [0.9.0] - 2024-12-12

### 🚀 Features

- Add proxy support

### 🚜 Refactor

- Add missing docstring in `utils.py`
- Improve readability of functions in `docstring.py`
- Improve readability by reordering functions in `settings.ts`

### ⚙️ Other

- Drop support for Python 3.8
- *(deps)* Bump python package `jedi` to 0.19.2
- Change name of `docstringFormat` option to `docstringStyle`
- Add sorting of settings
- Change ChatGPT prompt
- Add ignoring min length of commit body

## [0.8.0] - 2024-11-23

### 🚀 Features

- Add `gpt-4o` and `gpt-4o-mini` OpenAI models

### 🐛 Bug Fixes

- Formatting of LSP server init log message by adding missing `f` prefix

### 📚 Documentation

- *(readme)* Add `Table of Contents` section
- *(readme)* Add `Notice` section
- *(readme)* Add horizontal rules between sections
- *(readme)* Add subsections for `OpenAI API key` section

### ⚙️ Other

- Clarify that it is docstring generator for Python
- Move readme images to separate folder
- Update `.vscodeignore` file to be up-to-date

## [0.7.1] - 2024-05-05

### 🚀 Features

- Remove function indents from ChatGPT request

### 🚜 Refactor

- Reorganize structure of language server code

### ⚙️ Other

- Declare that untrusted workspaces are not supported with extension
- Configure `isort` and `flake8` via `pyproject.toml` file
- Create Python requirements file with development dependencies
- Update `.gitignore` file to be up-to-date
- Set `resource` as scope for extension configuration settings
- *(nox)* Remove deprecated code
- *(nox)* Add missing type annotations
- *(nox)* Format using Black
- *(nox)* Fix flake8 linter errors
- *(nox)* Reorganize structure of `lint` session code
- Add `pre-commit` framework to automatically check code before committing
- Set formatting python files when saving them
- Add `isort` and `black-formatting` extensions to recommendations

## [0.7.0] - 2024-04-16

### 🚀 Features

- Add `gpt-4` and `gpt-4-turbo` OpenAI models
- Add `onNewLine` option

### 🐛 Bug Fixes

- Remove new line for closing quotes of one-line docstring

### 📚 Documentation

- *(readme)* Make corrections for `Usage` section

### ⚙️ Other

- Drop `text-davinci-002` OpenAI model

## [0.6.1] - 2024-04-14

### 📚 Documentation

- *(readme)* Update demo animation for relevance
- *(readme)* Add screenshots for `Usage` section

### ⚙️ Other

- Change key bindings to shorter ones
- Change context menu group to `1_modification`
- Change title of docstring generation command for accuracy

## [0.6.0] - 2024-04-11

### 🚀 Features

- Remove function docstring and blank lines from ChatGPT request
- Add docstring completion provider triggered by `"""`

### 🐛 Bug Fixes

- Insertion position of generated docstring if another exists

### 📚 Documentation

- *(readme)* Add markdown formatting instead of quotes

### 🚜 Refactor

- Update variable names for clarity

### 🎨 Styling

- Fix flake8 linter errors

### ⚙️ Other

- Remove deprecated pylint directives

## [0.5.1] - 2023-09-27

### ⚙️ Other

- Increase default ChatGPT response timeout

## [0.5.0] - 2023-09-21

### 🚀 Features

- Add logging PID language server to output channel
- Add `showProgressNotification` option
- Add support for canceling docstring generation
- Add `responseTimeout` option

### 🚜 Refactor

- Change `chatgptPromptPattern` option name to `promptPattern`

### ⚙️ Other

- Disable automatic language server restart

## [0.4.0] - 2023-08-01

### 🚀 Features

- Add new command `Show Logs`
- Add support for language status reports

### 🚜 Refactor

- Reorganize structure of language server restart code

### ⚙️ Other

- Exclude some files from extension package
- Add check if interpreter path set in extension settings exists

## [0.3.3] - 2023-07-28

### 🐛 Bug Fixes

- Compatible with python 3.8

### ⚙️ Other

- Add resolver flag for correct dependency detection
- Update minimum supported python version to 3.8
- *(deps)* Bump python packages
- *(deps)* Bump nodejs packages
- Add notification when there is no compatible python interpreter

## [0.3.2] - 2023-07-27

### 🐛 Bug Fixes

- Jsonify OpenAI API key saving error
- Python server start with unsupported interpreter specified in extension settings

### ⚙️ Other

- Declare that Virtual Workspaces are not supported with extension
- Clarify error message of saving OpenAI API key to `SecretStorage`
- Add error handler for getting OpenAI API key from `SecretStorage`

## [0.3.1] - 2023-07-26

### 🐛 Bug Fixes

- Need to enter OpenAI API key for each docstring generation

## [0.3.0] - 2023-07-25

### 🚀 Features

- Add telemetry reporting

### 📚 Documentation

- *(readme)* Update header

### 🚜 Refactor

- Create new class for OpenAI API key storage functions
- Use `await` syntax instead of callback function

### 🎨 Styling

- Sort some python imports
- Format code with Prettier

### ⚙️ Other

- Change notification type when docstring cannot be added to source code
- Remove unnecessary error handler
- Add description of docstring generation LSP-request error to notification

## [0.2.2] - 2023-07-12

### 🐛 Bug Fixes

- Formatting docstring when ChatGPT returns it as MD code block

### ⚙️ Other

- Change ChatGPT system message to improve assistant behavior

## [0.2.1] - 2023-07-10

### 📚 Documentation

- *(readme)* Add link to extension on Visual Studio Marketplace
- *(readme)* Add OpenAI API key section

### ⚙️ Other

- Replace "docstrings" with "docstring" in extension name
- Clarify notification when docstring cannot be added to source code
- Add handler for OpenAI API Key saving error

## [0.2.0] - 2023-07-06

### 🚀 Features

- Move OpenAI API key from settings to secret storage

### 📚 Documentation

- *(readme)* Add spaces between shields
- *(readme)* Fix broken link for LICENSE
- *(changelog)* Add release date for version 0.1.0
