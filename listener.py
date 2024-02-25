import logging
import threading
import time

import sublime
import sublime_plugin

logger = logging.getLogger(__name__)


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
    def __init__(self, *args, **kwargs):
        logger.info("Initializing PyvoiceListener")
        self.trigger_info = TriggerInfo(
            last_tick=time.perf_counter(), view=None, last_event=time.perf_counter()
        )
        self.lock = threading.Lock()
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

    def loop_check_trigger(self):
        try:
            while True:
                if self.kill_switch:
                    return
                logger.debug(
                    "loop_check_trigger: acquiring lock from status %s",
                    self.lock.locked(),
                )
                with self.lock:
                    if self.should_update(self.trigger_info.view):
                        new_trigger_info = TriggerInfo(
                            last_tick=time.perf_counter(),
                            view=self.trigger_info.view,
                            last_event=self.trigger_info.last_event,
                            generate_imports=self.trigger_info.generate_imports,
                        )
                        self._update(
                            self.trigger_info.view, self.trigger_info.generate_imports
                        )
                        self.trigger_info = new_trigger_info
                logger.debug(
                    "loop_check_trigger: releasing lock to status %s and sleeping",
                    self.lock.locked(),
                )
                time.sleep(2.2)
        except Exception:
            logger.exception("loop_check_trigger: failure %s", lock.locked())

    def should_update(self, view):
        now = time.perf_counter()
        if (
            self._is_python(view)
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
        return view.file_name().endswith(".py")

    def _update(self, view, generate_imports=True):
        window = sublime.active_window()
        active_view = window.active_view()
        logger.info(
            "begining '%s' update of view %s %s %s %s %s %s",
            "full" if generate_imports else "partial",
            view,
            view.is_valid(),
            view.file_name(),
            view.window(),
            active_view,
            active_view.file_name(),
        )
        view.run_command(
            "lsp_execute",
            {
                "command_name": "get_spoken",
                "session_name": "LSP-pyvoice",
                "command_args": ["$file_uri", "$position", generate_imports],
            },
        )
        logger.debug(
            "finished update of view %s in window %s %s",
            view,
            window,
            window.is_valid(),
        )

    def _kick(self, view, generate_imports=True):
        logger.debug(
            "kicking %s %s %s %s",
            view,
            view.file_name(),
            generate_imports,
            self.lock.locked(),
        )
        logger.debug("is lock already in use? %s", self.lock.locked())
        with self.lock:
            now = time.perf_counter()
            logger.debug("acquired lock")
            new_trigger_info = TriggerInfo(
                last_tick=self.trigger_info.last_tick,
                view=view,
                last_event=now,
                generate_imports=generate_imports,
            )
            if self.trigger_info.last_event < new_trigger_info.last_event:
                logger.debug(
                    "updating from %s to %s", self.trigger_info, new_trigger_info
                )
                self.trigger_info = new_trigger_info

    def on_modified_async(self, view):
        self._kick(view, False)

    def on_load_async(self, view):
        self._kick(view)

    def on_reload_async(self, view):
        self._kick(view)

    def on_revert_async(self, view):
        self._kick(view)

    def on_activated_async(self, view):
        self._kick(view)
