import base64
import json
import logging
import os
from datetime import datetime
from multiprocessing.connection import Client

import sublime
import sublime_plugin
from LSP.plugin import register_plugin, unregister_plugin
from LSP.plugin.core.typing import Dict
from lsp_utils import notification_handler
from lsp_utils.pip_client_handler import PipClientHandler

from .ipc import send_notification

logger = logging.getLogger(__name__)


class Pyvoice(PipClientHandler):
    package_name = __package__
    requirements_txt_path = "requirements.txt"
    server_filename = "pyvoice"

    # --- PipClientHandler handlers ------------------------------------------------------------------------------------

    @classmethod
    def get_python_binary(cls) -> str:
        settings = sublime.load_settings("{}.sublime-settings".format(cls.package_name))
        python_binary = settings.get("python_binary")
        if python_binary and isinstance(python_binary, str):
            return python_binary
        if sublime.platform() == "windows":
            # with update to latest pygls got around the python3.11 and above crashing
            allowed_python_binaries = [
                os.path.expanduser(
                    r"~\AppData\Local\Programs\Python\Python312\python.exe"
                ),
                os.path.expanduser(
                    r"~\AppData\Local\Programs\Python\Python311\python.exe"
                ),
                os.path.expanduser(
                    r"~\AppData\Local\Programs\Python\Python310\python.exe"
                ),
                os.path.expanduser(
                    r"~\AppData\Local\Programs\Python\Python39\python.exe"
                ),
                os.path.expanduser(
                    r"~\AppData\Local\Programs\Python\Python38\python.exe"
                ),
            ]
            for python_binary in allowed_python_binaries:
                if os.path.isfile(python_binary):
                    return python_binary
        else:
            return "python3"
        # return super().get_python_binary()

    @classmethod
    def get_additional_variables(cls) -> Dict[str, str]:
        variables = super().get_additional_variables()
        variables.update(
            {
                "sublime_py_files_dir": os.path.dirname(sublime.__file__),
            }
        )
        return variables

    @notification_handler("voice/sendRpc")
    def m_voice_sendRpc(self, params):
        method = params["command"]
        cmd_params = params["params"]
        if not isinstance(method, str):
            raise ValueError("method must be a string")

        msg = method
        if method == "enhance_spoken":
            try:
                list_name = cmd_params[0]
                if isinstance(list_name, str):
                    msg = f"{method} ({list_name})"
            except IndexError:
                pass

        send_notification(method, cmd_params, log_msg=msg)


def plugin_loaded() -> None:
    register_plugin(Pyvoice)


def plugin_unloaded() -> None:
    unregister_plugin(Pyvoice)
