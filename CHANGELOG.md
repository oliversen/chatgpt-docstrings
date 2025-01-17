# Change Log

## 0.10.1 (2025-01-17)

- Improved formatting of generated docstring

## 0.10.0 (2024-12-25)

- Added support for different AI providers

## 0.9.2 (2024-12-18)

- Updated Python dependencies (pygls, openai)

## 0.9.1 (2024-12-13)

- Fixed HTTP proxy athorisation (`Proxy-Authorisation` header was not used)
- Updated Python dependencies (aiohttp, aiohttp-socks)

## 0.9.0 (2024-12-12)

- Added proxy support
- Updated Python dependencies (jedi)
- Dropped support for Python 3.8

## 0.8.0 (2024-11-20)

- Added `gpt-4o` and `gpt-4o-mini` OpenAI models
- Updated documentation
- Reduced extension size

## 0.7.1 (2024-05-05)

- Added removal of function indents from ChatGPT request
- Added instruction that untrusted workspaces are not supported with extension
- Changed scope of extension settings to all levels
- Performed code maintenance

## 0.7.0 (2024-04-16)

- Added `onNewLine` option
- Removed new line for closing quotes of one-line docstring
- Added `gpt-4` and `gpt-4-turbo` OpenAI models
- Dropped `text-davinci-002` OpenAI model
- Updated documentation

## 0.6.1 (2024-04-14)

- Updated documentation
- Changed key bindings

## 0.6.0 (2024-04-11)

- Added docstring completion provider triggered by `"""`
- Added removal of existing function docstring and blank lines from ChatGPT request
- Fixed wrong insertion position of generated docstring if another exists

## 0.5.1 (2023-09-27)

- Increased default ChatGPT response timeout

## 0.5.0 (2023-09-21)

- Changed `chatgptPromptPattern` option name to `promptPattern`
- Added `responseTimeout` option
- Added support for canceling docstring generation
- Added `showProgressNotification` option
- Added logging PID language server to output channel

## 0.4.0 (2023-08-02)

- Added support for language status reports
- Added new command `Show Logs`

## 0.3.3 (2023-07-28)

- Updated minimum supported Python version to 3.8
- Updated Python and Node.js dependencies

## 0.3.2 (2023-07-27)

- Fixed starting a python language server with an unsupported interpreter specified in the extension settings
- Fixed handling of an error when saving an OpenAI API key to the `SecretStorage`
- Added an error notification for getting an OpenAI API key from the `SecretStorage`

## 0.3.1 (2023-07-26)

- Fixed the need to enter an OpenAI API key for each docstring generation when it is not possible to save the key to the `SecretStorage`

## 0.3.0 (2023-07-25)

- Added telemetry reporting

## 0.2.2 (2023-07-12)

- Fixed formatting docstring when ChatGPT returns it as MD code block

## 0.2.1 (2023-07-11)

- Improved error notifications
- Added OpenAI API Key section to documentation

## 0.2.0 (2023-07-06)

- Moved OpenAI API key from settings to secret storage

## 0.1.0 (2023-07-03)

- The initial release
