from __future__ import annotations

import logging
import os
import sublime
from sublime_lib import ResourcePath

from LSP.plugin import LspPlugin, OnPreStartContext, notification_handler
from lsp_utils import UvVenvManager
from typing_extensions import override

from .ipc import send_notification

logger = logging.getLogger(__name__)


class Pyvoice(LspPlugin):

    @classmethod
    @override
    def on_pre_start_async(cls, context: OnPreStartContext) -> None:
        package_name = cls.plugin_storage_path.name
        UvVenvManager.on_pre_start_async(
            context, cls.plugin_storage_path, ResourcePath("Packages", package_name, 'server'), 'pyvoice')
        context.variables.update(
            {
                "sublime_py_files_dir": os.path.dirname(sublime.__file__),
            }
        )

    @notification_handler("voice/sendRpc")
    def on_voice_send_rpc(self, params) -> None:
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
    Pyvoice.register()


def plugin_unloaded() -> None:
    Pyvoice.unregister()
