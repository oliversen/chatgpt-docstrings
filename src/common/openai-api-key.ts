import * as vscode from 'vscode';
import { traceWarn } from './log/logging';
import { telemetryReporter } from './telemetry';

let _cashedKey: string | undefined = undefined;

export class OpenaiApiKey {
    private readonly secretId: string = 'openaiApiKey';
    private outputChannel: vscode.OutputChannel;
    private secretStorage: vscode.SecretStorage;

    constructor(outputChannel: vscode.OutputChannel, secretStorage: vscode.SecretStorage) {
        this.outputChannel = outputChannel;
        this.secretStorage = secretStorage;
    }

    public async get() {
        return _cashedKey || (_cashedKey = await this.secretStorage.get(this.secretId)) || (await this.set());
    }

    public async set() {
        const key = await this._ask();
        if (key) {
            _cashedKey = key;
            await this.secretStorage.store(this.secretId, key).then(undefined, (error) => {
                traceWarn('Failed to save OpenAI API Key: ', error);
                telemetryReporter.sendError('saveOpenaiApiKeyError', error.toJson());
                vscode.window
                    .showWarningMessage(
                        `Failed to save OpenAI API Key! See '${this.outputChannel.name}' output channel for details.`,
                        { title: 'Open Output', id: 1 },
                    )
                    .then((value) => {
                        if (value !== undefined && value.id === 1) {
                            this.outputChannel.show();
                        }
                    });
            });
        }
        return key;
    }

    private async _ask() {
        const prompt =
            'Please enter your OpenAI API key. You can get the key [here](https://platform.openai.com/account/api-keys).';
        const key = await vscode.window.showInputBox({
            prompt: prompt,
            validateInput: (text) => {
                if (!text) {
                    return prompt;
                } else {
                    return undefined;
                }
            },
        });
        return key;
    }
}
