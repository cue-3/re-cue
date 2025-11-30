import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Extension Activation Test Suite', () => {
  vscode.window.showInformationMessage('Start extension activation tests.');

  test('Extension should be present', () => {
    const ext = vscode.extensions.getExtension('cue-3.re-cue');
    assert.ok(ext, 'Extension should be found');
  });

  test('Extension should activate', async function() {
    this.timeout(10000); // Activation might take time
    
    const ext = vscode.extensions.getExtension('cue-3.re-cue');
    assert.ok(ext, 'Extension should exist');
    
    await ext?.activate();
    assert.ok(ext?.isActive, 'Extension should be active');
  });

  test('All commands should be registered', async function() {
    this.timeout(10000);
    
    // Ensure extension is activated
    const ext = vscode.extensions.getExtension('cue-3.re-cue');
    await ext?.activate();
    
    const commands = await vscode.commands.getCommands(true);
    
    // Core analysis commands
    assert.ok(commands.includes('recue.analyzeFile'), 'analyzeFile command should be registered');
    assert.ok(commands.includes('recue.analyzeFolder'), 'analyzeFolder command should be registered');
    assert.ok(commands.includes('recue.analyzeWorkspace'), 'analyzeWorkspace command should be registered');
    
    // Documentation generation commands
    assert.ok(commands.includes('recue.generateSpec'), 'generateSpec command should be registered');
    assert.ok(commands.includes('recue.generatePlan'), 'generatePlan command should be registered');
    assert.ok(commands.includes('recue.generateUseCases'), 'generateUseCases command should be registered');
    assert.ok(commands.includes('recue.generateDataModel'), 'generateDataModel command should be registered');
    assert.ok(commands.includes('recue.generateApiContract'), 'generateApiContract command should be registered');
    assert.ok(commands.includes('recue.generateDiagrams'), 'generateDiagrams command should be registered');
    assert.ok(commands.includes('recue.generateAll'), 'generateAll command should be registered');
    
    // Tree view refresh command (only one global refresh)
    assert.ok(commands.includes('recue.refreshResults'), 'refreshResults command should be registered');
  });

  test('Tree view providers should be registered', async function() {
    this.timeout(10000);
    
    // Ensure extension is activated
    const ext = vscode.extensions.getExtension('cue-3.re-cue');
    await ext?.activate();
    
    // Check that tree views are available (they should be registered)
    // We can't directly check the tree views, but we can verify the refresh command exists
    const commands = await vscode.commands.getCommands(true);
    assert.ok(commands.includes('recue.refreshResults'), 'refreshResults command should exist for tree views');
  });

  test('Configuration should have default values', () => {
    const config = vscode.workspace.getConfiguration('recue');
    
    // Check that configuration exists and has expected properties
    assert.ok(config.has('pythonPath'), 'pythonPath configuration should exist');
    assert.ok(config.has('outputDirectory'), 'outputDirectory configuration should exist');
    assert.ok(config.has('autoAnalyzeOnSave'), 'autoAnalyzeOnSave configuration should exist');
    assert.ok(config.has('enableHover'), 'enableHover configuration should exist');
    assert.ok(config.has('enableCodeLens'), 'enableCodeLens configuration should exist');
    assert.ok(config.has('verboseOutput'), 'verboseOutput configuration should exist');
    assert.ok(config.has('enableDirectParsing'), 'enableDirectParsing configuration should exist');
  });
});
