This is the sublime portion of 
<!-- MarkdownTOC  autolink="true" -->

- [Installation](#installation)
	- [Install the plugin](#install-the-plugin)
	- [Install the grammar](#install-the-grammar)
- [Settings](#settings)
- [Enabling or Disabling the plugin](#enabling-or-disabling-the-plugin)
- [Commands](#commands)

<!-- /MarkdownTOC -->

https://github.com/PythonVoiceCodingPlugin/pyvoice

# Installation

## Install the plugin

- Make sure you have [Package Control](https://packagecontrol.io/installation) installed in Sublime Text.

- This package is implemented as a language server and as a consequence depends on [LSP](https://packagecontrol.io/packages/LSP) . Install it via Package Control
	- Open the command palette `ctrl+shift+p` or `cmd+shift+p`
	- run `Package Control: Install Package`
	- search for `LSP` and install it

- Finally, install this package via Package Control using a custom repository
	- Open the command palette `ctrl+shift+p` or `cmd+shift+p`
	- run `Package Control: Add Repository`
	- paste the url of this repository: `https://github.com/PythonVoiceCodingPlugin/LSP-pyvoice`

- Restart Sublime Text and navigate to any python file, you should see these in the sidebar

## Install the grammar

- For talon use `https://github.com/PythonVoiceCodingPlugin/pyvoice_talon`

- For caster use `https://github.com/PythonVoiceCodingPlugin/pyvoice_caster`

# Settings

To edit the global settings click in the menu

`Preferences > Package Settings > LSP > Servers > LSP-pyvoice`

Or from the command palette `ctrl+shift+p` or `cmd+shift+p` run `Preferences: LSP-pyvoice Settings`

# Enabling or Disabling the plugin

The plugin is enabled by default. To disable it, open the command palette `ctrl+shift+p` or `cmd+shift+p` and run `LSP: Disable Language Server Globally`. Then choose `LSP-pyvoice` from the list of language servers. To enable it again, run `LSP: Enable Language Server Globally`.

If you want to disable it for a specific project, open the command palette `ctrl+shift+p` or `cmd+shift+p` and run `LSP: Disable Language Server in Project`. Then choose `LSP-pyvoice` from the list of language servers.  To enable it again, run `LSP: Enable Language Server in Project`.

To restart the language server, open the command palette `ctrl+shift+p` or `cmd+shift+p` and run `LSP: Restart Server`. Then choose `LSP-pyvoice` from the list of language servers.

All of this can also be accomplished via the menu `Tools > LSP  > Disable Language Server in Project` etc



# Commands

The following commands are available in the command palette `ctrl+shift+p` or `cmd+shift+p`

- `Preferences: LSP-pyvoice Settings`
- `LSP-pyvoice: Get Spoken` it allows you to manually trigger fetching spoken  information from the server
