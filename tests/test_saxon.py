import re

import pytest

from jsaxonpy import Xslt


def test_init():
    t = Xslt()
    assert t is not None


def test_transform(xml, xsl_copy):
    t = Xslt()
    out = t.transform(xml, xsl_copy)
    assert out == xml


def test_multiple_transforms(xml, xsl_copy):
    for _ in range(2):
        t = Xslt()
        out = t.transform(xml, xsl_copy)
        assert out == xml
        t2 = Xslt()
        out = t2.transform(xml, xsl_copy)
        assert out == xml


def test_transform_with_params(xml):
    params = {"param1": "value1", "param2": "value2"}
    xsl = """<xsl:stylesheet
            version="1.0"
            xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
        <xsl:param name="param1"/>
        <xsl:param name="param2"/>

        <xsl:template match="*">
            <xsl:copy>
                <xsl:attribute name="param1"><xsl:value-of select="$param1"/></xsl:attribute>
                <xsl:attribute name="param2"><xsl:value-of select="$param2"/></xsl:attribute>
            </xsl:copy>
            <xsl:copy-of select="."/>
        </xsl:template>

        </xsl:stylesheet>
    """
    expected = (
        """<?xml version="1.0" encoding="UTF-8"?><root param1="value1" param2="value2"/>"""
        """<root><child>Something</child></root>"""
    )
    t = Xslt()
    out = t.transform(xml, xsl, params)
    assert out == expected


def test_transform_exception_on_bad_xml(xsl_copy):
    xml = "<blah>"
    t = Xslt()
    with pytest.raises(t.jvm.jnius.JavaException) as e_info:
        t.transform(xml, xsl_copy)
    assert "XML document structures must start and end within the same entity." in str(e_info)


def test_transform_with_catalog(note_xml, xsl_copy, catalog):
    t = Xslt(catalog=catalog)
    if not t.is_catalog_supported:
        pytest.skip(f"catalog is not supported for Saxon {t.saxon_version}")

    out = t.transform(note_xml, xsl_copy)
    assert out == (
        """<?xml version="1.0" encoding="UTF-8"?>"""
        """<note><to>Tove</to><from>Jani</from>"""
        """<heading>Reminder</heading><body>Don\'t forget me this weekend!</body></note>"""
    )


def test_transform_without_catalog(note_xml, xsl_copy):
    t = Xslt()
    if not t.is_catalog_supported:
        pytest.skip(f"catalog is not supported for Saxon {t.saxon_version}")
    with pytest.raises(t.jvm.jnius.JavaException) as e_info:
        t.transform(note_xml, xsl_copy)
    assert "I/O error reported by XML parser processing" in str(e_info)


EXPECTED_VERSION_RE = re.compile(r"\d+(\.\d+){1,3}")


def test_saxon_version():
    t = Xslt()
    assert EXPECTED_VERSION_RE.match(t.saxon_version) is not None


def test_saxon_major_version():
    t = Xslt()
    assert t.saxon_major_version >= 9
