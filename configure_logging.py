import logging
import logging.config
import logging.handlers
import os

import sublime
import sublime_plugin

DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_LEVEL_NAME = logging.getLevelName(DEFAULT_LOG_LEVEL)
EVENT_LEVEL = logging.INFO


formatter = logging.Formatter(
    "%(name)s (sublime): %(levelname)s: %(message)s - %(asctime)s"
)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.NOTSET)

package_logger = logging.getLogger(__package__)
package_logger.addHandler(stream_handler)


logger = logging.getLogger(__name__)


def translate_to_log_level(level_name):
    level_name = level_name.upper()
    return {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
    }[level_name]


def _settings():
    return sublime.load_settings("LSP-pyvoice.sublime-settings")


def plugin_loaded():
    def on_settings_reload():
        cur_log_level = package_logger.getEffectiveLevel()
        new_log_level_name = (
            _settings().get("log_level", DEFAULT_LOG_LEVEL_NAME).upper()
        )
        new_log_level = translate_to_log_level(new_log_level_name)

        if new_log_level != cur_log_level:
            if cur_log_level > EVENT_LEVEL and new_log_level <= EVENT_LEVEL:
                # Only set level before emitting log event if it would not be seen otherwise
                package_logger.setLevel(new_log_level)
            cur_log_level_name = logging.getLevelName(cur_log_level)
            logger.log(
                EVENT_LEVEL,
                "Changing log level from %r to %r",
                cur_log_level_name,
                new_log_level_name,
            )
            package_logger.setLevel(new_log_level)  # Just set it again to be sure

    _settings().add_on_change(__name__, on_settings_reload)
    on_settings_reload()  # trigger on inital settings load, too


def plugin_unloaded():
    _settings().clear_on_change(__name__)
    package_logger.removeHandler(stream_handler)
