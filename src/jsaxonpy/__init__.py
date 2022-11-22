"""
    jsaxonpy - the python package to be used for your Java Saxon XSLT
    transformations in your python applications.
"""
import importlib.metadata

from .xslt import Xslt

try:
    __version__ = importlib.metadata.version(__package__ or __name__)
except importlib.metadata.PackageNotFoundError:
    # package is not installed
    pass

__revision__ = ""

__all__ = [Xslt]
