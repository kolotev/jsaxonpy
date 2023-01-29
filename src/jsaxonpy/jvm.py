import os

from .singleton import ProcessSingletonMeta


class JVM(metaclass=ProcessSingletonMeta):
    def __init__(self):
        import jnius_config

        jvm_options = os.getenv("JVM_OPTIONS", None)
        if not jnius_config.vm_running and jvm_options:
            jnius_config.add_options(*(jvm_options.split(" ")))
            # jnius_config.add_options("-Xmx2048m", "-XX:ActiveProcessorCount=4")
            # jnius_config.set_classpath(".", "/pmc/local/Saxon-J/saxon-he-11.4.jar")

        import jnius

        self.jnius = jnius
