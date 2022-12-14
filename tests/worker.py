from jsaxonpy import Xslt


def func(args):
    xml, xsl = args
    t = Xslt()
    out = t.transform(xml, xsl)
    return out
