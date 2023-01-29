import logging
from abc import ABC, abstractmethod
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional, Union

from .jvm import JVM
from .singleton import AbcThreadSingletonMeta

logger = logging.getLogger(__name__)

# minimum version of Saxon processor that supports catalog functionality
MIN_VERSION_SUPPORTING_CATALOG = 11

InputSource = Union[Path, str]
XsltParams = Dict[str, str]


class InterfaceXslt(ABC, metaclass=AbcThreadSingletonMeta):
    @abstractmethod
    def saxon_version(self) -> str:
        pass

    @abstractmethod
    def saxon_major_version(self) -> int:
        pass

    @abstractmethod
    def is_catalog_supported(self) -> bool:
        pass

    @abstractmethod
    def transform(
        self,
        xml: InputSource,
        xsl: InputSource,
        params: XsltParams = {},
        pretty: bool = False,
    ) -> str:
        pass


def _xslt_class_factory(jvm):  # noqa: ignore=C901
    # The following code was developed here because of peculiarities how
    # JVM starts and how to avoid it it starting in parent process,
    # of multiprocessing is used.
    autoclass = jvm.jnius.autoclass
    cast = jvm.jnius.cast

    # output related classes
    ByteArrayOutputStream = autoclass("java.io.ByteArrayOutputStream")
    File = autoclass("java.io.File")
    OutputStreamWriter = autoclass("java.io.OutputStreamWriter")
    StringReader = autoclass("java.io.StringReader")

    # saxon related classes
    Processor = autoclass("net.sf.saxon.s9api.Processor")
    QName = autoclass("net.sf.saxon.s9api.QName")
    SaxonVersion = autoclass("net.sf.saxon.Version")
    SerializerProperty = autoclass("net.sf.saxon.s9api.Serializer$Property")
    StreamSource = autoclass("javax.xml.transform.stream.StreamSource")
    XdmAtomicValue = autoclass("net.sf.saxon.s9api.XdmAtomicValue")
    XsltCompiler = autoclass("net.sf.saxon.s9api.XsltCompiler")
    XsltTransformer = autoclass("net.sf.saxon.s9api.XsltTransformer")

    class _Xslt(InterfaceXslt):
        def __init__(self, licensed_edition: bool, catalog: Optional[Path]):
            self._licensed_edition = licensed_edition
            self._catalog = catalog
            self._saxon_version = SaxonVersion.getProductVersion()
            self._processor = self._get_processor(licensed_edition, catalog)

        def _get_processor(self, licensed_edition: bool, catalog: Optional[Path]) -> Processor:
            # https://www.saxonica.com/html/documentation11/jvmdoc/net/sf/saxon/s9api/Processor.html
            # @argument is a boolean licensedEdition
            processor = Processor(licensed_edition)
            if isinstance(catalog, Path) and self.is_catalog_supported:
                processor.setCatalogFiles(str(catalog))
            return processor

        def _compiler(self) -> XsltCompiler:
            return self._processor.newXsltCompiler()

        @lru_cache(maxsize=32)
        def _transformer(self, source: InputSource) -> XsltTransformer:
            compiler = self._compiler()
            stream_source = self._stream_source(source)
            stylesheet = compiler.compile(stream_source)
            return stylesheet.load()

        def _set_param(self, transformer: XsltTransformer, name: str, value: str) -> None:
            qname = QName(name)
            transformer.setParameter(qname, XdmAtomicValue(value))
            if transformer.getParameter(qname) is None:
                logger.warning(
                    f"Verification of setting xsl param name={name} had failed, "
                    "trying to set it again."
                )
                self._set_param(transformer, name, value)

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
            output_serializer = self._processor.newSerializer(stream_writer)
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

        @property
        def saxon_version(self) -> str:
            return self._saxon_version

        @property
        def saxon_major_version(self) -> int:
            return int(self.saxon_version.split(".")[0])

        @property
        def is_catalog_supported(self) -> bool:
            return self.saxon_major_version >= MIN_VERSION_SUPPORTING_CATALOG

        def transform(
            self,
            xml: InputSource,
            xsl: InputSource,
            params: XsltParams = {},
            pretty: bool = False,
        ) -> str:
            #
            transformer = self._transformer(xsl)
            self._parse_xml(transformer, xml)
            self._set_params(transformer, params)
            output = self._set_output(transformer, pretty)
            transformer.transform()
            return output.toString()

    return _Xslt


class Xslt(InterfaceXslt):

    """
    Xslt class exposes transformations based on Java Saxon transform() method of
    net.sf.saxon.s9api.XsltTransformer class.

    Notes:
        If you plan to use multiprocessing, then do not instantiate Xslt class
        in parent process because saxon compiler hangs if parent process has jnius
        JVM machine running already.
    """

    def __init__(
        self,
        catalog: Optional[Path] = None,
        jvm: Optional[JVM] = None,
        licensed_edition: bool = False,
    ):
        """
        Initializer for Xslt class.

        Args:
            @catalog (Optional[Path], optional):
                Path to catalog file, optional. Defaults to None.
            @jvm (Optional[JVM], optional):
                optional instance of `JVM` class. Defaults to None.
            @licensed_edition (bool, optional):
                Indicate if you run on Licensed edition. Defaults to False.
        """
        self.jvm = jvm or JVM()
        XsltClass = _xslt_class_factory(self.jvm)
        self._xslt = XsltClass(licensed_edition=licensed_edition, catalog=catalog)

    @property
    def saxon_version(self):
        return self._xslt.saxon_version

    @property
    def saxon_major_version(self):
        return self._xslt.saxon_major_version

    @property
    def is_catalog_supported(self) -> bool:
        return self._xslt.is_catalog_supported

    def transform(
        self,
        xml: InputSource,
        xsl: InputSource,
        params: XsltParams = {},
        pretty: bool = False,
    ) -> str:
        """
        `transform` method executes the transformation of the input XML string
        or file with provided XSL code and optional XSL parameters.
        You can pass Stylesheet Export File (SEF) in place of `xsl` argument
        instead of regular XSL file path.

        Args:
            @xml (InputSource):
                XML markup (string) or file pathlib.Path("path/to/file.xml")
            @xsl (InputSource):
                XSL code (string) or file as pathlib.Path("path/to/file.xsl")
                or Stylesheet Export File (SEF).
            @params (XsltParams, optional):
                XSL parameters. Defaults to {}.
            @pretty (bool, optional):
                Format output pretty. Defaults to False.

        Returns:
            str: The output of the transformation

        Notes:
            The following types `InputSource`, `XsltParams` are defined as following:

            InputSource = Union[Path, str]
            XsltParams = Dict[str, str]


        """
        return self._xslt.transform(xml, xsl, params, pretty)
