"""
    jsaxonpy - the python package to be used for your Java Saxon XSLT
    transformations in your python applications.
"""
from importlib.metadata import version, PackageNotFoundError
from .xslt import Xslt

try:
    __version__ = version(__package__ or __name__)
except PackageNotFoundError:
    # package is not installed
    pass

__revision__ = ""

__all__ = [Xslt]
