# LSP-pyvoice

This is the sublime portion of [pyvoice](https://github.com/PythonVoiceCodingPlugin)


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
- [Inter Process Communication And Security Considerations](#inter-process-communication-and-security-considerations)
    - [Receiving commands from the voice coding framework](#receiving-commands-from-the-voice-coding-framework)
    - [Sending commands to the voice coding framework](#sending-commands-to-the-voice-coding-framework)
    - [Server Security](#server-security)
- [Enabling or Disabling the plugin](#enabling-or-disabling-the-plugin)
- [Commands](#commands)
- [Viewing Logs](#viewing-logs)
    - [Client Side logs](#client-side-logs)
    - [Full LSP traffic](#full-lsp-traffic)
- [Licensing And Acknowledgements](#licensing-and-acknowledgements)

<!-- /MarkdownTOC -->

# Features

This plugin is implemented as an [LSP](https://packagecontrol.io/packages/LSP) package and provides the following functionality

- it automatically manages installing and updating the [pyvoice](https://github.com/PythonVoiceCodingPlugin/pyvoice) for you in its own seperate virtual environment that lives inside sublime's storage path (see [lsp_utils](https://github.com/sublimelsp/lsp_utils/)

- it listens for user events, such as opening  a file, focusing a tab, editing its contents and appropriately triggers the server to generate hints mapping to their pronunciations items such as
    - expressions (properly formatted)
    - modules and symbols that can be imported

> [!TIP]
> for example, you have a local variable, called `server` and it has an attribute `project` which itself has has a method `get_environment`,
> then a speech hint would be generated, so that if the user says `server project get environment` , the voice coding system will insert `server.project.get_environment()`



> [!NOTE]
> At the moment, the plug-in would not trigger regeneration of speech hints if you change the current selection. These would be changed the future, but for the time being those cases you can triggered it manually via a command pallete cmd [belowv](#commands) or a voice command



- it provides the custom notification handlers to the sublime  LSP client, needed for receiving those speech hints, 

- it manages the communication with the programming by voice framework via IPC mechanism and forwards all necessary messages from the language server to the voice coding system


# Installation

## Pre-requisites

- Make sure you have some version of [Python](https://www.python.org/downloads/) >= 3.8 installed on your system. This is needed for installing and running the pyvoice executable

- Make sure you have [Package Control](https://packagecontrol.io/installation) installed in Sublime Text. If you install it for the first time, you may need to restart Sublime Text


- This package is implemented as a language server and as a consequence depends on [LSP](https://packagecontrol.io/packages/LSP) . Install it via Package Control
	- Open the command palette `ctrl+shift+p` or `cmd+shift+p`
	- run `Package Control: Install Package`
	- search for `LSP` and install it
    - depending on your build and version of LSP you install you may have to reboot sublime text

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
    "log_level":"warning",

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
        // Project settings used for configuring jedi Project

        // The base path where your python project is located.
        // Like all paths in this settings file it can be either
        // absolute or relative to the path of the sublime project.
        // By default, it resumed to be  the same folder that you have open
        // in the sublime window, but if your pipe and project is part
        // of a larger repository ,you should set this to the subdirectory 
        // containing your python code.for example:
        //      "project.path": "backend"
        "project.path": ".",

        // The path to the virtual environment for this project
        // again either absolute or relative to the sublime folder.
        // (NOT the project.path setting above)
        //
        // Furthermore, it could point either to the root of that environment,
        // or the python binary inside that environment 
        //      - "project.environmentPath": ".venv"
        //      - "project.environmentPath": ".venv/bin/python"
        //      - "project.environmentPath": ".venv\\Scripts\\python.exe"
        //
        //
        // WARNING
        //
        // while jedi will not execute python code from your code base
        // it WILL execute the python binary of the associated environment!
        // There are automated checks in place to guard against binaries 
        // that could for example have been injected by an attacker inside
        // vcs controlled files. You can find more about this mechanism in 
        //      https://jedi.readthedocs.io/en/latest/_modules/jedi/api/environment.html
        //      under the _is_safe function.
        //
        // However, it is still a good idea to only point this setting
        // to environments that you trust.
        "project.environmentPath": null,

        // A list of paths to override the sys path if needed.
        // Leave this null to generate sys.path from the environment.
        // WARNING: This will COMPLETELY override the sys.path 
        // generated from the environment.
        "project.sysPath": null,

        // Adds these paths at the end of the sys path.
        "project.addedSysPath": [],

        // If enabled (default), adds paths from local directories.
        // Otherwise, you will have to rely on your packages being properly configured on the sys.path.
        "project.smartSysPath": true,



        // Hints.Imports settings


        // Enable or disable the generation of stdlib imports.
        "hints.imports.stdlib.enabled": true,


        // Enable or disable the generation of third-party imports.
        // Pyvoice will try to automatically discover the  dependencies 
        // of your project  and  is going
        // to generate hints for their modules. In order to do so,pyvoice
        // will try:
        //
        // - pep621 dependencies in pyproject.toml
        // - poetry dependencies in pyproject.toml
        // - options.install_requires in setup.cfg
        // - traditional requirements.txt
        // 
        // NOTE: By default hints would be generated ONLY for your top level dependencies
        // aka distributions that you directly depend on, not transiet dependencies.
        "hints.imports.thirdParty.enabled": true,

        // A list of third-party distributions to include modules from.
        "hints.imports.thirdParty.includeDists": [],

        // A list of third-party distributions to exclude.
        "hints.imports.thirdParty.excludeDists": [],



        // Enable or disable the generation of project imports.
        // This generator is going to scan your project folders
        // recursively for pure python modules and generate hints for them.
        // This is performed in a manner somewhat similar to setuptools 
        //  - if the project follows a source layout, the src/ folder would be scanned
        //  - if the projects follow flat layout, hints would be generated
        //    for top level modules and recursively for top level packages
        //    that match the filters used by setuptools.discover
        //  - the explicit layout, where user maps in their pyproject.toml
        //    a set of packages/module names to folders containg their respective
        //    respective code is not supported to yet
        "hints.imports.project.enabled": true,

        // Enable or disable the generation of import hints for symbols
        // So far, all of the imports hints generators are targeting modules
        // However, there are cases where symbols like functions or classes
        // that are used so frequently in your project
        // that you want to be able to import them in a single step
        // and without having to speak the name of the containing module
        //
        // For example you might want to be able to speak
        //      `import optional`
        // in order to insert
        //      `from typing import Optional`
        //
        // The explicit symbols generator allows you to define a 
        // list of modules that you want to generate hints for their symbols
        "hints.imports.explicitSymbols.enabled": true,

        // A list of modules to generate hints hints for their defined symbols.
        "hints.imports.explicitSymbols.modules": ["typing"],



        // Hints.Expressions settings


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



        // Logging settings
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


so for example if you want to point pyvoice to a virtual environment your sublime-project file  might look like this

```json
{
    "settings":
    {
        "LSP":
        {
            "LSP-pyvoice":
            {
                "settings":
                {
                    "project.environmentPath": ".venv"
                }
            },
        },

    },
}
```

or to see debug logs from the server

```json
{
    "settings":
    {
        "LSP":
        {
            "LSP-pyvoice":
            {
                "settings":
                {
                    "logging.level": "DEBUG"
                }
            },
        },

    },
}
```


# Inter Process Communication And Security Considerations

## Receiving commands from the voice coding framework

Commands to execute in sublime (like adding an import statement to a file) are sent from the voice coding framework via the [sublime command line interface](https://www.sublimetext.com/docs/command_line.html).



## Sending commands to the voice coding framework

In order to transmit speech hints to the programming by voice system, an interprocess communication mechanism is employed utilizing `AF_UNIX` sockets on UNIX systems and `AF_PIPE` named pipes on Windows as transports with the format   being JSON-RPC 2.0. The programming by voice system binds those sockets or pipes as a listener/server and sublime connects as a client.

> [!NOTE]
> In order to keep implementation as simple and as stateless as possible, connections are intentionally short-lived, one per notification sent, and only target one voice system at a time.

> [!IMPORTANT]
> Implementation wise, the sublime client is going to utilize the stdlib `multiprocessing.connection` machinery, which also features a mechanism for authenticating both ends of the connection via cryptographic challenge based on a shared key. That is important because there exists a race condition where processes running with lower privileges may try to bind the named pipe on windows before the voice coding system does, thus causing sublime to talk to them instead.
> The shared key is generated by the voice system and is persisted in json file in the user's home directory, which should be out of reach for those low privilege user processes. That being said,due to the one way direction RPC is flowing, the attack surface should be pretty limited even without the auth mechanism


> [!WARNING]
> Unfortunately, the auth handshake employed by the stdlib(3.8) is using HMAC-MD5. It is only python 3.12 that introduced support for stronger hash functions , while also extending the handshake protocol in a backwards compatible manner. While not the end of the world, at some point,I would have to back port the improved version via monkey patching

## Server Security

Please take a look at the [security considerations for the server as well](https://github.com/PythonVoiceCodingPlugin/pyvoice-language-server?tab=readme-ov-file#security-considerations)



# Enabling or Disabling the plugin

The plugin is enabled by default. To disable it, open the command palette `ctrl+shift+p` or `cmd+shift+p` and run `LSP: Disable Language Server Globally`. Then choose `LSP-pyvoice` from the list of language servers. To enable it again, run `LSP: Enable Language Server Globally`.

If you want to disable it for a specific project, open the command palette `ctrl+shift+p` or `cmd+shift+p` and run `LSP: Disable Language Server in Project`. Then choose `LSP-pyvoice` from the list of language servers.  To enable it again, run `LSP: Enable Language Server in Project`.

To restart the language server, open the command palette `ctrl+shift+p` or `cmd+shift+p` and run `LSP: Restart Server`. Then choose `LSP-pyvoice` from the list of language servers.

All of this can also be accomplished via the menu `Tools > LSP  > Disable Language Server in Project` etc



# Commands

The following commands are available in the command palette `ctrl+shift+p` or `cmd+shift+p`

- `Preferences: LSP-pyvoice Settings`
- `LSP-pyvoice: Get Spoken` allows you to manually trigger fetching spoken  information from the server


# Viewing Logs

<!-- ## Language Server logs
## Client Side logs
 -->

## Full LSP traffic

To view full traffic, from the command palette (`ctrl+shift+p` or `cmd+shift+p`) run `LSP: Toggle Log Panel` or via right click at the box in the down left corner

![](https://github.com/PythonVoiceCodingPlugin/assets/sublime/traffic_open.png)

you should see a panel like this

![](https://github.com/PythonVoiceCodingPlugin/assets/sublime/traffic_logs.png)



# Licensing And Acknowledgements

The project is licensed under the GPLv3. I should point out that I have templated upon [LSP-pylsp](https://github.com/sublimelsp/LSP-pylsp) for the project structure and directly borrowed some logging related code from [PackagedDev](https://github.com/SublimeText/PackageDev/blob/master/) and as a consequence those bits are licensed according to their respected projects licenses!

Also worth noting, inspiration for this project was [SublimeTalon](https://github.com/trishume/SublimeTalon/blob/master/sublime_talon.py) though by now there is barely any shared code left.
