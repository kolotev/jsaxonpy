import abc
import threading


class ProcessSingletonMeta(type):
    _class_instance = None
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not cls._class_instance:
            with cls._lock:
                if not cls._class_instance:
                    cls._class_instance = super().__call__(*args, **kwargs)
        return cls._class_instance


tsm_cache = threading.local()  # Cache for ThreadSingletonMeta instances


class ThreadSingletonMeta(type):
    def __call__(cls, *args, **kwargs):
        global tsm_cache
        vars(tsm_cache).setdefault("items", {})

        item_key = hash((cls, id(None)) + args + (id(None),) + tuple(sorted(kwargs.items())))
        if not tsm_cache.items.get(item_key):
            tsm_cache.items[item_key] = super().__call__(*args, **kwargs)

        return tsm_cache.items[item_key]


class AbcThreadSingletonMeta(ThreadSingletonMeta, abc.ABCMeta):
    pass
