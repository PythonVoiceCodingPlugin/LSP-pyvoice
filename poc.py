import os

import sublime
import toml
from LSP.plugin import AbstractPlugin, register_plugin, unregister_plugin


class Pyvoice(AbstractPlugin):
    package_name = __package__
    requirements_txt_path = "requirements.txt"
    server_filename = "pyvoice"

    @classmethod
    def name(cls) -> str:
        return "pyvoice"

    @classmethod
    def basedir(cls) -> str:
        return os.path.join(cls.storage_path(), __package__)

    @classmethod
    def server_version(cls) -> str:
        return "0.0.0"

    @classmethod
    def current_server_version(cls) -> str:
        return "0.0.0"

    @classmethod
    def needs_update_or_installation(cls) -> bool:
        return False

    @classmethod
    def install_or_update(cls) -> None:
        return

    def m_voice_sendRpc(self, params):
        from SublimeVoice import api
        if isinstance(params["params"], list):
            api.send_voice_async(params["command"], *params["params"])
        else:
            api.send_voice_async(params["command"], **params["params"])


def plugin_loaded() -> None:
    register_plugin(Pyvoice)


def plugin_unloaded() -> None:
    unregister_plugin(Pyvoice)
