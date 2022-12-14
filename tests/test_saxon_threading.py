from concurrent.futures import ThreadPoolExecutor

from .worker import func


def test_threading(xml, xsl_copy):

    with ThreadPoolExecutor(max_workers=3) as executor:
        for out in executor.map(func, ((xml, xsl_copy),) * 10):
            assert out == xml
