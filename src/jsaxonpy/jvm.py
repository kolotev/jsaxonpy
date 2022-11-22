import os

from .signleton import Singleton


class JVM(metaclass=Singleton):
    def __init__(self):
        jvm_options = os.getenv("JVM_OPTIONS", "").split(" ")
        if jvm_options:
            import jnius_config

            if not jnius_config.vm_running:
                jnius_config.add_options(*(jvm_options))
                # jnius_config.add_options("-Xrs", "-Xmx512m", "-XX:ActiveProcessorCount=4")
                # jnius_config.set_classpath(".", "/pmc/local/Saxon-J/saxon-he-11.4.jar")

        import jnius

        self.jnius = jnius
