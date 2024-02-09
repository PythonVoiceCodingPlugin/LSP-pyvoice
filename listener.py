import time

import sublime
import sublime_plugin


class PyvoiceListener(sublime_plugin.EventListener):
    def __init__(self):
        self.last_tick = 0.0

    def _update(self, view, generate_imports=True):
        view.run_command(
            "lsp_execute",
            {
                "command_name": "get_spoken",
                "session_name": "LSP-pyvoice",
                "command_args": ["$file_uri", "$position", generate_imports],
            },
        )

    def _kick(self, view, generate_imports=True):
        # print("view", view)
        if view is None:
            return

        now = time.perf_counter()
        nice = 3.0
        # print("_kick", view, now, "last", self.last_tick)
        if now < self.last_tick + nice:
            return
        self.last_tick = now
        self._update(view, generate_imports)

    def on_modified_async(self, view):
        self._kick(view, False)

    def on_load_async(self, view):
        self._kick(view)

    def on_activated_async(self, view):
        self._kick(view)
