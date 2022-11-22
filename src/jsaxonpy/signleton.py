import threading


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        thread_id = threading.get_native_id()
        instances = cls._instances.setdefault(thread_id, {})
        if cls not in instances:
            instances[cls] = super().__call__(*args, **kwargs)

        return instances[cls]
