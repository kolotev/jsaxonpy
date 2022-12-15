from concurrent.futures import ProcessPoolExecutor

import pytest

from .worker import func


def test_multiprocessing(xml, xsl_copy):
    import jnius_config

    if jnius_config.vm_running:
        pytest.fail(
            "JVM is already running, "
            "you need to start tests in a separate process.\n"
            "Use --forked option."
        )
    with ProcessPoolExecutor(max_workers=3) as executor:
        for out in executor.map(func, ((xml, xsl_copy),) * 10):
            assert out == xml
