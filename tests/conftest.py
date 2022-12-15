from pathlib import Path

import pytest

xsl_copy_ = """<xsl:stylesheet
            version="1.0"
            xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

        <xsl:template match="/">
            <xsl:copy-of select="."/>
        </xsl:template>

        </xsl:stylesheet>
    """
xml_ = """<?xml version="1.0" encoding="UTF-8"?><root><child>Something</child></root>"""


@pytest.fixture
def xsl_copy():
    return xsl_copy_


@pytest.fixture
def xml():
    return xml_


@pytest.fixture
def catalog():
    return Path(__file__).parent / "fixtures" / "catalog.xml"


@pytest.fixture
def note_xml():
    return Path(__file__).parent / "fixtures" / "note.xml"
