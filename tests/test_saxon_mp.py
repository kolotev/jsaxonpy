from concurrent.futures import ProcessPoolExecutor

from jsaxonpy import Xslt


def func(args):
    xml, xsl = args
    t = Xslt()
    out = t.transform(xml, xsl)
    return out


def test_multiprocessing(xml, xsl_copy):

    with ProcessPoolExecutor(max_workers=3) as executor:
        for out in executor.map(func, ((xml, xsl_copy),) * 10):
            assert out == xml
