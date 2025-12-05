/**
 * ty Server Manager
 * 
 * Handles discovery and management of ty executable for LSP integration.
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

/**
 * Find the ty executable in the environment
 * 
 * Search order:
 * 1. User-configured path (re-cue.ty.path setting)
 * 2. Virtual environment (VIRTUAL_ENV/bin/ty)
 * 3. Workspace .venv directory
 * 4. Python extension's selected interpreter directory
 * 5. Global PATH (which ty / where ty)
 */
export async function findTyExecutable(): Promise<string | undefined> {
    // 1. Check user configuration
    const config = vscode.workspace.getConfiguration('re-cue.ty');
    const configuredPath = config.get<string>('path');
    if (configuredPath) {
        if (await isExecutable(configuredPath)) {
            return configuredPath;
        }
    }

    // 2. Check VIRTUAL_ENV
    const virtualEnv = process.env.VIRTUAL_ENV;
    if (virtualEnv) {
        const tyPath = path.join(virtualEnv, 'bin', 'ty');
        if (await isExecutable(tyPath)) {
            return tyPath;
        }
    }

    // 3. Check workspace .venv
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (workspaceFolders) {
        for (const folder of workspaceFolders) {
            const venvPath = path.join(folder.uri.fsPath, '.venv', 'bin', 'ty');
            if (await isExecutable(venvPath)) {
                return venvPath;
            }
        }
    }

    // 4. Check Python extension's interpreter
    try {
        const pythonExtension = vscode.extensions.getExtension('ms-python.python');
        if (pythonExtension) {
            if (!pythonExtension.isActive) {
                await pythonExtension.activate();
            }
            const pythonPath = pythonExtension.exports?.settings?.getExecutionDetails?.()?.execCommand?.[0];
            if (pythonPath) {
                const interpreterDir = path.dirname(pythonPath);
                const tyPath = path.join(interpreterDir, 'ty');
                if (await isExecutable(tyPath)) {
                    return tyPath;
                }
            }
        }
    } catch (error) {
        // Python extension not available or failed to query
    }

    // 5. Check global PATH
    try {
        const { stdout } = await execAsync(process.platform === 'win32' ? 'where ty' : 'which ty');
        const tyPath = stdout.trim().split('\n')[0];
        if (tyPath && await isExecutable(tyPath)) {
            return tyPath;
        }
    } catch (error) {
        // ty not found in PATH
    }

    return undefined;
}

/**
 * Check if a file exists and is executable
 */
async function isExecutable(filePath: string): Promise<boolean> {
    try {
        await fs.promises.access(filePath, fs.constants.X_OK);
        return true;
    } catch {
        return false;
    }
}

/**
 * Get ty version
 */
export async function getTyVersion(tyPath: string): Promise<string | undefined> {
    try {
        const { stdout } = await execAsync(`"${tyPath}" --version`);
        return stdout.trim();
    } catch (error) {
        return undefined;
    }
}

/**
 * Check if ty LSP is supported (ty >= 0.0.1a31)
 */
export async function isTyLspSupported(tyPath: string): Promise<boolean> {
    const version = await getTyVersion(tyPath);
    if (!version) {
        return false;
    }

    // ty LSP support was added in 0.0.1a31
    // Version format: ty 0.0.1a31
    const match = version.match(/ty\s+(\d+)\.(\d+)\.(\d+)(?:a(\d+))?/);
    if (!match) {
        return false;
    }

    const [, major, minor, patch, alpha] = match.map(Number);
    
    // Must be at least 0.0.1a31
    if (major > 0) return true;
    if (minor > 0) return true;
    if (patch > 1) return true;
    if (patch === 1 && alpha && alpha >= 31) return true;

    return false;
}
