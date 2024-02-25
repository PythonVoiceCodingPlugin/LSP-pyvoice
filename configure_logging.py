import logging
import logging.config
import logging.handlers
import os

import sublime
import sublime_plugin

packages_path = sublime.packages_path()
root_path = os.path.dirname(packages_path)
log_file = os.path.join(root_path, "Log", "pyvoice.log")

package_logger = logging.getLogger(__package__)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)
package_logger.addHandler(stream_handler)

debug_formatter = logging.Formatter(
    "%(asctime)s - %(name)24s - %(threadName)12s - %(thread)5d - %(levelname)8s - %(message)s"
)
file_handler = logging.handlers.RotatingFileHandler(
    log_file, maxBytes=1024 * 1024, backupCount=5
)
file_handler.setFormatter(debug_formatter)
file_handler.setLevel(logging.DEBUG)
package_logger.addHandler(file_handler)

package_logger.setLevel(logging.DEBUG)
package_logger.propagate = False
