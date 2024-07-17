import logging
import os

import sublime
import sublime_plugin

logger = logging.getLogger(__name__)


def get_caster_user_dir():
    """this should be using appdirs instead but whatever"""
    if "CASTER_USER_DIR" in os.environ:
        return os.environ["CASTER_USER_DIR"]
    elif os.name == "nt":
        return os.path.expanduser("~\\AppData\\Local\\caster")
    else:
        return os.path.expanduser("~/.local/share/caster")


def get_rules_from_caster_directory(caster_user_dir):
    if not caster_user_dir or not os.path.exists(caster_user_dir):
        return None
    old_style = os.path.join(caster_user_dir, "rules")
    new_style = os.path.join(caster_user_dir, "caster_user_content", "rules")
    for directory in [new_style, old_style]:
        if os.path.exists(directory):
            return directory
    else:
        return None


def get_talon_user_directory():
    if os.name == "nt":
        return os.path.expanduser("~\\AppData\\Roaming\\talon")
    else:
        return os.path.expanduser("~/.talon")


def get_rules_from_talon_directory(talon_user_dir):
    if not talon_user_dir or not os.path.exists(talon_user_dir):
        return None
    rules_directory = os.path.join(talon_user_dir, "user")
    if os.path.exists(rules_directory):
        return rules_directory
    else:
        return None


class QuickInstallGrammarsCommand(sublime_plugin.WindowCommand):
    def run(self, payload):
        if not payload:
            sublime.error_message(
                "No grammars found. Please make sure Caster and Talon are installed."
            )
            return
        directory = payload["directory"]
        directory_name = payload["directory_name"]
        url = payload["url"]
        if not os.path.exists(directory):
            sublime.error_message(
                "Directory {directory} does not exist.".format(directory=directory)
            )
            return
        if os.path.exists(os.path.join(directory, directory_name)):
            sublime.error_message(
                "Directory {directory} already contains subdirectory {directory_name}".format(
                    directory=directory, directory_name=directory_name
                )
            )
            return
        self.window.run_command(
            "exec",
            {
                "cmd": ["git", "clone", url, directory_name],
                "working_dir": os.path.expanduser("~\\Downloads"),
            },
        )
        self.window.run_command("hide_panel")
        sublime.message_dialog("Successfully installed grammars.")

    def input(self, args):
        return QuickInstallGrammarsInputHandler()


def get_caster_payload():
    caster_user_dir = get_caster_user_dir()
    caster_rules_directory = get_rules_from_caster_directory(caster_user_dir)
    if not caster_rules_directory:
        return None
    return {
        "directory": caster_rules_directory,
        "directory_name": "pyvoice_caster",
        "url": "https://github.com/PythonVoiceCodingPlugin/pyvoice_caster",
    }


def get_talon_payload():
    talon_user_dir = get_talon_user_directory()
    talon_rules_directory = get_rules_from_talon_directory(talon_user_dir)
    if not talon_rules_directory:
        return None
    return {
        "directory": talon_rules_directory,
        "directory_name": "pyvoice_talon",
        "url": "https://github.com/PythonVoiceCodingPlugin/pyvoice_talon",
    }


class QuickInstallGrammarsInputHandler(sublime_plugin.ListInputHandler):
    def name(self):
        return "payload"

    def placeholder(self):
        return "Select the directory containing the grammars"

    def list_items(self):
        caster_payload = get_caster_payload()
        talon_payload = get_talon_payload()
        logger.info("Caster payload: %s", caster_payload)
        logger.info("Talon payload: %s", talon_payload)
        if hasattr(sublime, "ListInputItem"):
            return [
                sublime.ListInputItem(
                    text="Caster",
                    details=caster_payload["directory"],
                    value=caster_payload,
                ),
                sublime.ListInputItem(
                    text="Talon",
                    details=talon_payload["directory"],
                    value=talon_payload,
                ),
            ]
        else:
            return [
                ("Caster" + " " + caster_payload["directory"], caster_payload),
                ("Talon" + " " + talon_payload["directory"], talon_payload),
            ]

    def confirm(self, value):
        return value


