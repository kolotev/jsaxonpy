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
        assert "XML document structures must start and end within the same entity." in e_info
