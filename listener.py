import logging
import threading
import time

import sublime
import sublime_plugin

logger = logging.getLogger(__name__)

from LSP.plugin.core.registry import windows
from LSP.plugin.core.types import FEATURES_TIMEOUT, debounced


class TriggerInfo:
    def __init__(self, last_tick, view, last_event, generate_imports=True):
        super(TriggerInfo, self).__init__()
        self.last_tick = last_tick
        self.view = view
        self.last_event = last_event
        self.generate_imports = generate_imports

    def __str__(self):
        return "TriggerInfo(last_tick={}, view={}, filename={}, last_event={}, generate_imports={})".format(
            self.last_tick,
            self.view,
            self.view.file_name() if self.view is not None else None,
            self.last_event,
            self.generate_imports,
        )

    __repr__ = __str__


class PyvoiceListener(sublime_plugin.EventListener):
    def __init__(self, *args, **kwargs):
        logger.info("Initializing PyvoiceListener")
        self.trigger_info = TriggerInfo(
            last_tick=time.perf_counter(), view=None, last_event=time.perf_counter()
        )
        self.cv = threading.Condition()
        self.kill_switch = False
        self.thread = threading.Thread(
            target=self.loop_check_trigger, name="LoopThread"
        )
        self.thread.start()
        super(PyvoiceListener, self).__init__(*args, **kwargs)

    def __del__(self):
        self.kill_switch = True
        self.thread.join(1.0)
        super(PyvoiceListener, self).__del__()

    def single_update_attempt(self):
        logger.debug("Beggining single update attempt")
        try:
            with self.cv:
                self.cv.wait_for(self.should_update)
                logger.debug("Should update satisfied from %s", self.trigger_info)
                new_trigger_info = TriggerInfo(
                    last_tick=time.perf_counter(),
                    view=self.trigger_info.view,
                    last_event=self.trigger_info.last_event,
                    generate_imports=self.trigger_info.generate_imports,
                )
                self._update(self.trigger_info.view, self.trigger_info.generate_imports)
                self.trigger_info = new_trigger_info
        except Exception:
            logger.exception("Error during single update attempt:")

    def loop_check_trigger(self):
        while not self.kill_switch:
            self.single_update_attempt()
            time.sleep(3)

    def should_update(self):
        now = time.perf_counter()
        view = self.trigger_info.view
        if (
            self._is_foreground(view)
            and self._is_python(view)
            and self.trigger_info.last_tick < now - 3.0
            and self.trigger_info.last_tick < self.trigger_info.last_event
        ):
            return True
        return False

    def _is_python(self, view):
        if view is None:
            return False
        if view.element() is not None:
            return False
        if view.file_name() is None:
            return False
        wm = windows.lookup(view.window())
        if wm is None:
            return False
        session = wm.get_session("LSP-pyvoice", view.file_name())
        return session is not None

    def _is_foreground(self, view):
        window = sublime.active_window()
        active_view = window.active_view()
        return view == active_view and view.is_valid()

    def _update(self, view, generate_imports=True):
        logger.info(
            "begining '%s' update of view %s %s",
            "FULL" if generate_imports else "PARTIAL",
            view,
            view.file_name(),
        )
        view.run_command(
            "lsp_execute",
            {
                "command_name": "get_spoken",
                "session_name": "LSP-pyvoice",
                "command_args": ["$file_uri", "$position", generate_imports],
            },
        )
        logger.debug("finished update of view %s in window %s", view, view.window())

    def _kick(self, view, generate_imports=True, timestamp=None):
        now = timestamp or time.perf_counter()
        new_trigger_info = TriggerInfo(
            last_tick=self.trigger_info.last_tick,
            view=view,
            last_event=now,
            generate_imports=generate_imports,
        )
        logger.debug("new event %s", new_trigger_info)
        with self.cv:
            logger.debug(
                "lock aqcuired - comparing %s against %s",
                new_trigger_info,
                self.trigger_info,
            )
            if self.trigger_info.last_event < new_trigger_info.last_event:
                self.trigger_info = new_trigger_info
                logger.debug("notifying loop thread")
                self.cv.notify()
            else:
                logger.debug("no-op")

    def on_modified_async(self, view):
        timestamp = time.perf_counter()
        change_count = view.change_count()
        debounced(
            lambda: self._kick(view, False, timestamp=timestamp),
            FEATURES_TIMEOUT,
            lambda: view.is_valid() and change_count == view.change_count(),
            async_thread=True,
        )

    def on_load_async(self, view):
        self._kick(view)

    def on_reload_async(self, view):
        self._kick(view)

    def on_revert_async(self, view):
        self._kick(view)

    def on_activated_async(self, view):
        self._kick(view)
