# LSP-pyvoice

This is the sublime portion of [pyvoice](https://github.com/PythonVoiceCodingPlugin/pyvoice)


<div>
<img src="https://github.com/PythonVoiceCodingPlugin/assets/blob/main/pyvoice_logo.png" align="right" height=320 width=320/>
</div>

<!-- MarkdownTOC  autolink="true" -->

- [Features](#features)
- [Installation](#installation)
    - [Pre-requisites](#pre-requisites)
    - [Install the plugin](#install-the-plugin)
    - [Install the grammar](#install-the-grammar)
- [Settings](#settings)
    - [Default settings](#default-settings)
    - [Editing settings globally](#editing-settings-globally)
    - [Editing settings per project](#editing-settings-per-project)
- [Enabling or Disabling the plugin](#enabling-or-disabling-the-plugin)
- [Commands](#commands)
- [Viewing Logs](#viewing-logs)
    - [Event Listener logs](#event-listener-logs)
    - [LSP traffic](#lsp-traffic)
    - [Server logs](#server-logs)
- [Licensing And Acknowledgements](#licensing-and-acknowledgements)

<!-- /MarkdownTOC -->

# Features

It is implemented as an [LSP](https://packagecontrol.io/packages/LSP) package and provides the following functionality

- it automatically manages installing and updating the [pyvoice](https://github.com/PythonVoiceCodingPlugin/pyvoice) for you in its own seperate virtual environment

- it provides the customizations to the sublime  LSP client, needed for receiving speech hints, etc from the language server

- it manages the communication with the programming by voice framework

# Installation

## Pre-requisites

- Make sure you have some version of [Python](https://www.python.org/downloads/) >= 3.8 installed on your system. This is needed for installing and running the pyvoice executable

- Make sure you have [Package Control](https://packagecontrol.io/installation) installed in Sublime Text.

- This package is implemented as a language server and as a consequence depends on [LSP](https://packagecontrol.io/packages/LSP) . Install it via Package Control
	- Open the command palette `ctrl+shift+p` or `cmd+shift+p`
	- run `Package Control: Install Package`
	- search for `LSP` and install it

## Install the plugin

Finally, install this package via Package Control using a custom repository
	- Open the command palette `ctrl+shift+p` or `cmd+shift+p`
	- run `Package Control: Add Repository`
	- paste the url of this repository: `https://github.com/PythonVoiceCodingPlugin/LSP-pyvoice`

Restart Sublime Text and navigate to any python file, you should see these in the sidebar

## Install the grammar

- For talon use `https://github.com/PythonVoiceCodingPlugin/pyvoice_talon`

- For caster use `https://github.com/PythonVoiceCodingPlugin/pyvoice_caster`

# Settings

The project builts on top of the standard [LSP client configuration](https://lsp.sublimetext.io/client_configuration/) 

## Default settings

```json
{
    // the command that actually launches the server process
    // leave this as is to use the automatically installed
    // pyvoice language server
    "command": [
        "$server_path"
    ],

    // the python interpreter to use for installing and running
    // the pyvoice language server. it should be 3.8 and above
    // pypy may also work. If null, the plug-in will try to
    // automatically pick a suitable interpreter
    "python_binary": null,

    // environment variables to set when running the language server
    "env": {},

    // set the log level for the CLIENT SIDE code of the plugin
    // for example these will produce logs concerning 
    // - the interprocess communication with the programming 
    //   by voice framework
    // - when the plug-in chooses to synchronize spoken hints
    //   by sending a request to the language server and 
    //   forrewarding them to the programming by voice system
    // etc..
    // it does not affect the level of the logs
    // that the language server produces itself like
    // - any errors detected during semantic analysis
    // - metadata about the hints that it generates
    // etc..
    "log_level":"WARNING",


    // selectors to match the files that the language server
    // is responsible for
    "selector": "source.python",
    // ST3
    "languages": [
        {
            "languageId": "python",
            "scopes": [
                "source.python"
            ],
            "syntaxes": [
                "Packages/Python/Python.sublime-syntax"
            ],
        }
    ],

    // a set of settings/config that will be sent to the language server
    // via workspace/didChangeConfiguration notification
    // or retrieved by the workspace/configuration server side request.
    // these allow you to customize how pyvoice processes each of your projects
    "settings": {
        // The base path where your python project is located.
        // Like all paths in this settings file it can be either
        // absolute or relative to the path of the sublime project.
        "project.path": ".",

        // The path to the root of the virtual environment
        // again either absolute or relative to the sublime project path.
        "project.environmentPath": null,

        // A list of paths to override the sys path if needed.
        // WARNING: This will COMPLETELY override the sys.path.
        // Leave this null to generate sys.path from the environment.
        "project.sysPath": null,

        // Adds these paths at the end of the sys path.
        "project.addedSysPath": [],

        // If enabled (default), adds paths from local directories.
        // Otherwise, you will have to rely on your packages being properly configured on the sys.path.
        "project.smartSysPath": true,

        // Enable or disable the generation of stdlib imports.
        "hints.imports.stdlib.enabled": true,

        // Settings for customizing the generation of hints hints for
        // third-party modules. Pyvoice will try to automatically
        // discover the  dependencies of your project  and  is going
        // to generate hints for their modules. In order to do so,pyvoice
        // will try:
        // - pep621 dependencies in pyproject.toml
        // - poetry dependencies in pyproject.toml
        // - options.install_requires in setup.cfg
        // - traditional requirements.txt
        // NOTE: By default hints would be generated ONLY for your top level dependencies
        // aka distributions that you directly depend on, not transiet dependencies.
        // default behavior is not satisfactory you can add/exclude
        // distributions from the settings below.

        // Enable or disable the generation of third-party imports.
        "hints.imports.thirdParty.enabled": true,

        // A list of third-party distributions to include modules from.
        "hints.imports.thirdParty.includeDists": [],

        // A list of third-party distributions to exclude.
        "hints.imports.thirdParty.excludeDists": [],

        // Enable or disable the generation of project imports.
        "hints.imports.project.enabled": true,

        // Enable or disable the generation of explicit symbols.
        "hints.imports.explicitSymbols.enabled": true,

        // A list of modules to generate hints hints for their defined symbols.
        "hints.imports.explicitSymbols.modules": ["typing"],

        // Enable or disable the generation of hints hints for local scope.
        "hints.expressions.locals.enabled": true,
        // Hints from param names of the signatures of local scope variables. 
        "hints.expressions.locals.signature": true,

        // Enable or disable the generation of hints hints for non-local scope.
        "hints.expressions.nonlocals.enabled": true,
        // Hints from param names of the signatures of non-local scope variables. 
        "hints.expressions.nonlocals.signature": true,

        // Enable or disable the generation of hints hints for global scope.
        "hints.expressions.globals.enabled": true,
        // Hints from param names of the signatures of global scope variables. 
        "hints.expressions.globals.signature": true,

        // Enable or disable the generation of hints hints for built-in scope.
        "hints.expressions.builtins.enabled": true,
        // Hints from param names of the signatures of built-in scope variables. 
        "hints.expressions.builtins.signature": true,

        // An upper bound on the number of expressions to generate.
        "hints.expressions.limit": 2000,

        // Set the logging level for the pyvoice executable.
        "logging.level": "INFO"
    }
}
```



## Editing settings globally

To edit the global settings click in the menu

`Preferences > Package Settings > LSP > Servers > LSP-pyvoice`

Or from the command palette `ctrl+shift+p` or `cmd+shift+p` run `Preferences: LSP-pyvoice Settings`

## Editing settings per project

To edit the settings for a specific project, click in the menu

`Project > Edit Project`

and add the following settings

```json
{
	"settings":
	{
		"LSP":
		{
			"LSP-pyvoice":
			{
				// your customizations go in here
			},
		},

	},
}
```


# Enabling or Disabling the plugin

The plugin is enabled by default. To disable it, open the command palette `ctrl+shift+p` or `cmd+shift+p` and run `LSP: Disable Language Server Globally`. Then choose `LSP-pyvoice` from the list of language servers. To enable it again, run `LSP: Enable Language Server Globally`.

If you want to disable it for a specific project, open the command palette `ctrl+shift+p` or `cmd+shift+p` and run `LSP: Disable Language Server in Project`. Then choose `LSP-pyvoice` from the list of language servers.  To enable it again, run `LSP: Enable Language Server in Project`.

To restart the language server, open the command palette `ctrl+shift+p` or `cmd+shift+p` and run `LSP: Restart Server`. Then choose `LSP-pyvoice` from the list of language servers.

All of this can also be accomplished via the menu `Tools > LSP  > Disable Language Server in Project` etc



# Commands

The following commands are available in the command palette `ctrl+shift+p` or `cmd+shift+p`

- `Preferences: LSP-pyvoice Settings`
- `LSP-pyvoice: Get Spoken` it allows you to manually trigger fetching spoken  information from the server


# Viewing Logs

## Event Listener logs
## LSP traffic
## Server logs



# Licensing And Acknowledgements

The project is licensed under the GPLv3. I should point out that I have heavily upon [LSP-pylsp](https://github.com/sublimelsp/LSP-pylsp) for the project structure and directly borrowed some logging related code from [PackagedDev](https://github.com/SublimeText/PackageDev/blob/master/) and as a consequence those bits are licensed according to their respected projects licenses!

Also worth noting, inspiration for this project was [SublimeTalon](https://github.com/trishume/SublimeTalon/blob/master/sublime_talon.py) though by now there is barely any shared code left.
