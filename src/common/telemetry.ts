import TelemetryReporter from '@vscode/extension-telemetry';
import * as vscode from 'vscode';
import { LanguageClient } from 'vscode-languageclient/node';

const appInsightsKey = 'fb5a34af-bc76-40b8-8e9f-b962d1ac2615';

enum TelemetryType {
    info = 'info',
    error = 'error',
}

interface TelemetryParams {
    type: TelemetryType;
    name: string;
    [data: string]: string;
}

class Reporter extends TelemetryReporter {
    public sendInfo(name: string, data: any): void {
        const dataTrusted = new vscode.TelemetryTrustedValue(data);
        // @ts-ignore
        this.sendTelemetryEvent(name, { infoData: dataTrusted });
    }

    public sendError(name: string, data: any): void {
        const dataTrusted = new vscode.TelemetryTrustedValue(data);
        // @ts-ignore
        this.sendTelemetryErrorEvent(name, { errorData: dataTrusted });
    }

    public configureOnTelemetry(lsClient: LanguageClient) {
        lsClient.onTelemetry((params: TelemetryParams) => {
            switch (params.type as TelemetryType) {
                case TelemetryType.info:
                    this.sendInfo(params.name, params.data);
                    break;
                case TelemetryType.error:
                    this.sendError(params.name, params.data);
                    break;
            }
        });
    }
}

export const telemetryReporter = new Reporter(appInsightsKey);
