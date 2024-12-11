// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

import { ConfigurationChangeEvent, ConfigurationScope, WorkspaceConfiguration, WorkspaceFolder } from 'vscode';
import { getInterpreterDetails } from './python';
import { getConfiguration, getWorkspaceFolders } from './vscodeapi';

export interface ISettings {
    cwd: string;
    workspace: string;
    interpreter: string[];
    openaiModel: string;
    docstringStyle: string;
    onNewLine: boolean;
    promptPattern: string;
    responseTimeout: number;
    showProgressNotification: boolean;
    proxy: IProxy;
}

interface IProxy {
    url: string;
    authorization: string;
    strictSSL: boolean;
}

function getProxy(namespace: string): IProxy {
    const defaultProxy = {
        url: '',
        authorization: '',
        strictSSL: false,
    };
    const getProxyConfig = (config: WorkspaceConfiguration): IProxy => ({
        url: config.get<string>(`proxy`) ?? defaultProxy.url,
        authorization: config.get<string>(`proxyAuthorization`) ?? defaultProxy.authorization,
        strictSSL: config.get<boolean>(`proxyStrictSSL`) ?? defaultProxy.strictSSL,
    });
    const extConfig = getConfiguration(namespace);
    const httpConfig = getConfiguration('http');
    const extProxy = getProxyConfig(extConfig);
    const appProxy = getProxyConfig(httpConfig);
    const proxySupport = httpConfig.get<string>('proxySupport') ?? '';

    if (!extProxy.url && proxySupport !== 'off' && appProxy.url) {
        return appProxy;
    }
    return extProxy;
}

function resolveVariables(value: string[], workspace?: WorkspaceFolder): string[] {
    const substitutions = new Map<string, string>();
    const home = process.env.HOME || process.env.USERPROFILE;
    if (home) {
        substitutions.set('${userHome}', home);
    }
    if (workspace) {
        substitutions.set('${workspaceFolder}', workspace.uri.fsPath);
    }
    substitutions.set('${cwd}', process.cwd());
    getWorkspaceFolders().forEach((w) => {
        substitutions.set('${workspaceFolder:' + w.name + '}', w.uri.fsPath);
    });

    return value.map((s) => {
        for (const [key, value] of substitutions) {
            s = s.replace(key, value);
        }
        return s;
    });
}

function getGlobalValue<T>(config: WorkspaceConfiguration, key: string, defaultValue: T): T {
    const inspect = config.inspect<T>(key);
    return inspect?.globalValue ?? inspect?.defaultValue ?? defaultValue;
}

export function getInterpreterFromSetting(namespace: string, scope?: ConfigurationScope) {
    const config = getConfiguration(namespace, scope);
    return config.get<string[]>('interpreter');
}

export function getExtensionSettings(namespace: string, includeInterpreter?: boolean): Promise<ISettings[]> {
    return Promise.all(getWorkspaceFolders().map((w) => getWorkspaceSettings(namespace, w, includeInterpreter)));
}

export async function getWorkspaceSettings(
    namespace: string,
    workspace: WorkspaceFolder,
    includeInterpreter?: boolean,
): Promise<ISettings> {
    const config = getConfiguration(namespace, workspace.uri);

    let interpreter: string[] = [];
    if (includeInterpreter) {
        interpreter = getInterpreterFromSetting(namespace, workspace) ?? [];
        if (interpreter.length === 0) {
            interpreter = (await getInterpreterDetails(workspace.uri)).path ?? [];
        }
    }

    const workspaceSetting = {
        cwd: workspace.uri.fsPath,
        workspace: workspace.uri.toString(),
        interpreter: resolveVariables(interpreter, workspace),
        openaiModel: config.get<string>(`openaiModel`) ?? 'gpt-4o-mini',
        docstringStyle: config.get<string>(`docstringStyle`) ?? 'google',
        onNewLine: config.get<boolean>(`onNewLine`) ?? false,
        promptPattern:
            config.get<string>(`promptPattern`) ??
            'Generate docstring in {docstring_style} style for python function below:\n{function}',
        responseTimeout: config.get<number>(`responseTimeout`) ?? 15,
        showProgressNotification: config.get<boolean>(`showProgressNotification`) ?? true,
        proxy: getProxy(namespace),
    };
    return workspaceSetting;
}

export async function getGlobalSettings(namespace: string, includeInterpreter?: boolean): Promise<ISettings> {
    const config = getConfiguration(namespace);

    let interpreter: string[] = [];
    if (includeInterpreter) {
        interpreter = getGlobalValue<string[]>(config, 'interpreter', []);
        if (interpreter === undefined || interpreter.length === 0) {
            interpreter = (await getInterpreterDetails()).path ?? [];
        }
    }

    const setting = {
        cwd: process.cwd(),
        workspace: process.cwd(),
        interpreter: interpreter,
        openaiModel: getGlobalValue<string>(config, 'openaiModel', 'gpt-4o-mini'),
        docstringStyle: getGlobalValue<string>(config, 'docstringStyle', 'google'),
        onNewLine: getGlobalValue<boolean>(config, `onNewLine`, false),
        promptPattern: getGlobalValue<string>(
            config,
            'promptPattern',
            'Generate docstring in {docstring_style} style for python function below:\n{function}',
        ),
        responseTimeout: getGlobalValue<number>(config, 'responseTimeout', 15),
        showProgressNotification: getGlobalValue<boolean>(config, `showProgressNotification`, true),
        proxy: getProxy(namespace),
    };
    return setting;
}

export function checkIfConfigurationChanged(e: ConfigurationChangeEvent, namespace: string): boolean {
    const settings = [
        `${namespace}.interpreter`,
        `${namespace}.openaiModel`,
        `${namespace}.docstringStyle`,
        `${namespace}.onNewLine`,
        `${namespace}.promptPattern`,
        `${namespace}.responseTimeout`,
        `${namespace}.proxy`,
        `${namespace}.proxyAuthorization`,
        `${namespace}.proxyStrictSSL`,
        `http.proxy`,
        `http.proxyAuthorization`,
        `http.proxyStrictSSL`,
        `http.proxySupport`,
    ];
    const changed = settings.map((s) => e.affectsConfiguration(s));
    return changed.includes(true);
}
