JSaxonPy
========

[![PyPI](https://img.shields.io/pypi/v/jsaxonpy.svg)]()

jsaxonpy - the python package to be used for your Java Saxon XSLT
transformations in your python applications.


Installation
------------

```
pip install jsaxonpy
```

Quick overview
--------------

```python
>>> from jsaxonpy import Xslt
>>> t = Xslt()
>>> xml = "<root><child>text</child></root>"
>>> xsl = """
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/">
    <xsl:copy-of select="."/>
  </xsl:template>
</xsl:stylesheet>
"""
>>> t.transform(xml, xsl)
'<?xml version="1.0" encoding="UTF-8"?><root><child>text</child></root>'
```

You can supply params if you needed as python dictioary with keys & values as strings (`str` type).
```
>>> params = {"param1": "value1", "param2": "value2"}
>>> out = t.transform(xml, xsl, params)
 ```

`xml` and `xsl` arguments could be either string documents (`str` type) or
files names wrapped into pathlib.Path(...) class, before being passed.

Also you can run transformations using threads or multiple processes using
concurrent.futures or multiprocessing modules. The only known limitation is
not to run transformations (using `Xslt` class) using multi-processing in parent
process, you can successfully run it in children. If you try to run in parent process and in children processes, then you application would hang. With threading instantiation of `Xslt` class works both in main thread and in children threads.

Examples
========

Plain
-----
```python
from pathlib import Path

from jsaxonpy import Xslt


t = Xslt()
xml = Path("file.xml")
xsl = Path("file.xsl")
print(t.transform(xml, xsl))
```
would produce:
```
<?xml version="1.0" encoding="UTF-8"?><root><child>text</child></root>
```

Threads
-------
```python
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from jsaxonpy import Xslt

def func(args):
    xml, xsl = args
    t = Xslt()
    out = t.transform(xml, xsl)
    return out

xsl_path = Path('file.xsl')
worker_args = []

with ThreadPoolExecutor(max_workers=3) as executor:
  for xml_path in map(lambda f: Path(f), ["file1.xml", ..., "fileN.xml"]):
    worker_args.append((xml_path, xsl_path))
    for out in executor.map(func, worker_args):
      assert out == xml
```

Processes
---------
```python
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from jsaxonpy import Xslt

def func(args):
    xml, xsl = args
    t = Xslt()
    out = t.transform(xml, xsl)
    return out

xsl_path = Path('file.xsl')
worker_args = []

with ProcessPoolExecutor(max_workers=3) as executor:
  for xml_path in map(lambda f: Path(f), ["file1.xml", ..., "fileN.xml"]):
    worker_args.append((xml_path, xsl_path))
    for out in executor.map(func, worker_args):
      assert out == xml
```

GCP Functions
-------------
```python
import os, threading
from timeit import default_timer as timer

import functions_framework

from jdk4py import JAVA, JAVA_HOME, JAVA_VERSION
from saxonhe4py import SAXON_HE_JAR
from jsaxonpy import Xslt

# following env variable must be defined, otherwise pyjnius would fail
os.environ["JAVA_HOME"] = str(JAVA_HOME)
os.environ["JDK_HOME"] = str(JAVA_HOME)

# to find the location of Saxon HE
os.environ["CLASSPATH"] = str(SAXON_HE_JAR)

# setup JVM options
os.environ["JVM_OPTIONS"] = "-Xmx64m"


@functions_framework.http
def transform(request):
    #
    thread_id = threading.get_native_id()
    process_id = os.getpid()

    #
    timer_xslt_started = timer()
    t = Xslt() # do not move this from function.
    timer_xslt_ended = timer()

    #
    xml = "<p>Paragraph text</p>"
    xsl = """
    <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
      <xsl:copy-of select="."/>
    </xsl:template>
    </xsl:stylesheet>
    """

    #
    timer_transform_started = timer()
    output=t.transform(xml, xsl)
    timer_transform_ended = timer()

    return (
      f"{output}\n"
      f"timer(Xslt)      = {timer_xslt_ended - timer_xslt_started:.6f}\n"
      f"timer(transform) = {timer_transform_ended - timer_transform_started:.6f}\n"
      f"thread_id={thread_id} process_id={process_id}\n"
    )
```

Notes
=====

The following versions of Saxon were tested 9, 10, 11.

XML Catalog resolution is available for Saxon 11.

Before executing you application it is expected you set your java related
environment variables, including the `CLASSPATH` to point to your Java Saxon
installation.

You can use `JVM_OPTIONS` environment variable to set java virtual environment,
see example below.

```bash
export JVM_OPTIONS="-Xrs -Xmx4096m -XX:ActiveProcessorCount=24";
export CLASSPATH=/usr/local/Saxon-J/saxon-he-11.4.jar;
your_python_app.py
```

When you pass the same xsl path it is actually being compiled once for the
time of the life of the process/thread, which means you do not need to do
any special steps to compile those to speed up transformations.

Development note
----------------

Based on github issue [Passing PythonJavaClass object to Java method/class does
not increase Python ref counter ](https://github.com/kivy/pyjnius/issues/345)
to avoid undefined values passed to Saxon code (JVM) it is suggested to assign
Python's autoclass or cast derivatives `PythonJavaClass` to python variables.
An example:

instead of:
```python
transformer.setParameter(QName(name), XdmAtomicValue(value))
```

write:
```python
qname= QName(name)
xdm_atomic_value = XdmAtomicValue(value)
transformer.setParameter(qname, xdm_atomic_value)
```

API
===

class JVM
---------
```
 1 Help on class JVM in module jsaxonpy.jvm:
 2
 3 class JVM(builtins.object)
 4  |  JVM(*args, **kwargs)
 5  |
 6  |  Methods defined here:
 7  |
 8  |  __init__(self)
 9  |      Initialize self.  See help(type(self)) for accurate signature.
10  |
```

class Xslt
----------

```
 1 Help on class Xslt in module jsaxonpy.xslt:
 2
 3 class Xslt(InterfaceXslt)
 4  |  Xslt(catalog: Optional[pathlib.Path] = None, jvm: Optional[jsaxonpy.jvm.JVM] = None, licensed_edition: bool = False)
 5  |
 6  |  Xslt class exposes transformations based on Java Saxon transform() method of
 7  |  net.sf.saxon.s9api.XsltTransformer class.
 8  |
 9  |  Notes:
10  |      If you plan to use multiprocessing, then do not instantiate Xslt class
11  |      in parent process because saxon compiler hangs if parent process has jnius
12  |      JVM machine running already.
13  |
14  |  Method resolution order:
15  |      Xslt
16  |      InterfaceXslt
17  |      abc.ABC
18  |      builtins.object
19  |
20  |  Methods defined here:
21  |
22  |  __init__(self, catalog: Optional[pathlib.Path] = None, jvm: Optional[jsaxonpy.jvm.JVM] = None, licensed_edition: bool = False)
23  |      Initializer for Xslt class.
24  |
25  |      Args:
26  |          @catalog (Optional[Path], optional):
27  |              Path to catalog file, optional. Defaults to None.
28  |          @jvm (Optional[JVM], optional):
29  |              optional instance of `JVM` class. Defaults to None.
30  |          @licensed_edition (bool, optional):
31  |              Indicate if you run on Licensed edition. Defaults to False.
32  |
33  |  transform(self, xml: Union[pathlib.Path, str], xsl: Union[pathlib.Path, str], params: Dict[str, str] = {}, pretty: bool = False) -> str
34  |      `transform` method executes the transformation of the input XML string
35  |      or file with provided XSL code and optional XSL parameters.
36  |      You can pass Stylesheet Export File (SEF) in place of `xsl` argument instead
37  |      of regular XSL file path.
38  |
39  |      Args:
40  |          @xml (InputSource):
41  |              XML markup (string) or file pathlib.Path("path/to/file.xml")
42  |          @xsl (InputSource):
43  |              XSL code (string) or file pathlib.Path("path/to/file.xsl")
44  |          @params (XsltParams, optional):
45  |              XSL parameters. Defaults to {}.
46  |          @pretty (bool, optional):
47  |              Format output pretty. Defaults to False.
48  |
49  |      Returns:
50  |          str: The output of the transformation
51  |
52  |      Notes:
53  |          The following types `InputSource`, `XsltParams` are defined as following:
54  |
55  |          InputSource = Union[Path, str]
56  |          XsltParams = Dict[str, str]
57  |
58  |  ----------------------------------------------------------------------
59  |  Readonly properties defined here:
60  |
61  |  is_catalog_supported
62  |
63  |  saxon_major_version
64  |
65  |  saxon_version
66  |
```