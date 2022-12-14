from concurrent.futures import ProcessPoolExecutor

from .worker import func


def test_multiprocessing(xml, xsl_copy):

    with ProcessPoolExecutor(max_workers=3) as executor:
        for out in executor.map(func, ((xml, xsl_copy),) * 10):
            assert out == xml
