import functools
import threading
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Union

from .jvm import JVM

InputSource = Union[Path, str]
XsltParams = Dict[str, str]


class InterfaceXslt(ABC):
    @abstractmethod
    def transform(
        self, xml: InputSource, xsl: InputSource, params: XsltParams = {}, pretty: bool = False
    ) -> str:
        pass


def _construct_Xslt_class(jvm, cache_maxsize):  # noqa: ignore=C901
    # The following code was developed here because of peculiarities how
    # JVM starts and how to avoid it it starting in parent process,
    # of multiprocessing is used.
    autoclass = jvm.jnius.autoclass
    cast = jvm.jnius.cast

    # output related classes
    ByteArrayOutputStream = autoclass("java.io.ByteArrayOutputStream")
    OutputStreamWriter = autoclass("java.io.OutputStreamWriter")
    StringReader = autoclass("java.io.StringReader")
    File = autoclass("java.io.File")

    # saxon related classes
    Processor = autoclass("net.sf.saxon.s9api.Processor")
    QName = autoclass("net.sf.saxon.s9api.QName")
    SerializerProperty = autoclass("net.sf.saxon.s9api.Serializer$Property")
    StreamSource = autoclass("javax.xml.transform.stream.StreamSource")
    XdmAtomicValue = autoclass("net.sf.saxon.s9api.XdmAtomicValue")
    XsltTransformer = autoclass("net.sf.saxon.s9api.XsltTransformer")

    class _Xslt(InterfaceXslt):
        def __init__(self, licensed_edition):
            self._licensed_edition = licensed_edition

        def _processor(self):
            # https://www.saxonica.com/html/documentation11/jvmdoc/net/sf/saxon/s9api/Processor.html
            # @argument is a boolean licensedEdition
            return Processor(self._licensed_edition)

        def _compiler(self):
            return self._processor().newXsltCompiler()

        @functools.lru_cache(maxsize=cache_maxsize)
        def _transformer(self, source, thread_id=threading.get_native_id()) -> XsltTransformer:
            compiler = self._compiler()
            stream_source = self._stream_source(source)
            stylesheet = compiler.compile(stream_source)

            return stylesheet.load()

        def _set_param(self, transformer: XsltTransformer, name: str, value: str) -> None:
            transformer.setParameter(QName(name), XdmAtomicValue(value))

        def _set_params(self, transformer: XsltTransformer, dict_: XsltParams) -> None:
            transformer.clearParameters()
            for name, value in dict_.items():
                self._set_param(transformer, name, value)

        def _parse_xml(self, transformer: XsltTransformer, source: InputSource) -> None:
            xml_stream = self._stream_source(source)
            transformer.setSource(xml_stream)

        def _set_output(self, transformer: XsltTransformer, pretty: bool) -> ByteArrayOutputStream:
            output_stream = ByteArrayOutputStream()
            stream_writer = OutputStreamWriter(output_stream)
            output_serializer = self._processor().newSerializer(stream_writer)
            INDENT = SerializerProperty.INDENT
            output_serializer.setOutputProperty(INDENT, "yes" if pretty else "no")
            transformer.setDestination(output_serializer)

            return output_stream

        def _is_not_xml(self, source: str) -> bool:
            return str.find(source, "<") == -1 or str.find(source, ">") == -1

        def _stream_source(self, source: InputSource) -> StreamSource:
            if isinstance(source, str) and self._is_not_xml(source):
                raise ValueError("You source string does not look like an XML document")

            elif isinstance(source, str):
                reader = StringReader(source)
                stream_source = StreamSource(cast("java.io.Reader", reader))

            elif isinstance(source, Path):
                stream_source = StreamSource(File(str(source)))

            else:
                raise ValueError(
                    f"Unsupported value type `{type(source)}` for `source` argument, "
                    f"only {InputSource} is supported."
                )

            return stream_source

        def transform(
            self,
            xml: InputSource,
            xsl: InputSource,
            params: XsltParams = {},
            pretty: bool = False,
        ) -> str:

            transformer = self._transformer(xsl)
            output = self._set_output(transformer, pretty)
            self._parse_xml(transformer, xml)
            self._set_params(transformer, params)
            transformer.transform()

            #
            return output.toString()

    return _Xslt


# if you plan to use multiprocessing, then do not instantiate Xslt class
# in parent process because saxon compiler hangs if parent process has jnius
# JVM machine running.
class Xslt(InterfaceXslt):
    """ """

    def __init__(self, licensed_edition=False, jvm=None, cache_maxsize=32):
        self.jvm = jvm or JVM()
        self._xslt = _construct_Xslt_class(self.jvm, cache_maxsize)(licensed_edition)

    def transform(
        self,
        xml: InputSource,
        xsl: InputSource,
        params: XsltParams = {},
        pretty: bool = False,
    ) -> str:

        return self._xslt.transform(xml, xsl, params, pretty)
