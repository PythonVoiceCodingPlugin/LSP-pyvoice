import threading
import time

import sublime
import sublime_plugin


class TriggerInfo:
    def __init__(self, last_tick, view, last_event, generate_imports=True):
        super(TriggerInfo, self).__init__()
        self.last_tick = last_tick
        self.view = view
        self.last_event = last_event
        self.generate_imports = generate_imports

    def __str__(self):
        return "TriggerInfo(last_tick={}, view={}, last_event={}, generate_imports={})".format(
            self.last_tick, self.view, self.last_event, self.generate_imports
        )

    __repr__ = __str__


class PyvoiceListener(sublime_plugin.EventListener):
    def __init__(self):
        self.trigger_info = TriggerInfo(
            last_tick=time.perf_counter(), view=None, last_event=time.perf_counter()
        )
        self.lock = threading.RLock()
        self.thread = threading.Thread(target=self.loop_check_trigger)
        self.thread.start()

    def __del__(self):
        self.thread.join(1.0)
        super(PyvoiceListener, self).__del__()

    def loop_check_trigger(self):
        while True:
            with self.lock:
                now = time.perf_counter()
                if (
                    self.trigger_info.view is not None
                    and self.trigger_info.last_tick < now - 3.0
                    and self.trigger_info.last_tick < self.trigger_info.last_event
                ):
                    new_trigger_info = TriggerInfo(
                        last_tick=now,
                        view=self.trigger_info.view,
                        last_event=self.trigger_info.last_event,
                        generate_imports=self.trigger_info.generate_imports,
                    )
                    self._update(
                        self.trigger_info.view, self.trigger_info.generate_imports
                    )
                    self.trigger_info = new_trigger_info
            time.sleep(0.2)

    def _update(self, view, generate_imports=True):
        print("Pyvoice: begining update", view, view.file_name(), generate_imports)
        view.run_command(
            "lsp_execute",
            {
                "command_name": "get_spoken",
                "session_name": "LSP-pyvoice",
                "command_args": ["$file_uri", "$position", generate_imports],
            },
        )

    def _kick(self, view, generate_imports=True):
        with self.lock:
            now = time.perf_counter()
            new_trigger_info = TriggerInfo(
                last_tick=self.trigger_info.last_tick,
                view=view,
                last_event=now,
                generate_imports=generate_imports,
            )
            if self.trigger_info.last_event < new_trigger_info.last_event:
                self.trigger_info = new_trigger_info

    def on_modified_async(self, view):
        self._kick(view, False)

    def on_load_async(self, view):
        self._kick(view)

    def on_activated(self, view):
        self._kick(view)
