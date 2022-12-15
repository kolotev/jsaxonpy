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

Supported and tested versions of Saxon are 9, 10, 11.

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
 4  |  Xslt(cache_maxsize: int = 32, catalog: Optional[pathlib.Path] = None, jvm: Optional[jsaxonpy.jvm.JVM] = None, licensed_edition: bool = False      4 )
 5  |
 6  |  # if you plan to use multiprocessing, then do not instantiate Xslt class
 7  |  # in parent process because saxon compiler hangs if parent process has jnius
 8  |  # JVM machine running.
 9  |
10  |  Method resolution order:
11  |      Xslt
12  |      InterfaceXslt
13  |      abc.ABC
14  |      builtins.object
15  |
16  |  Methods defined here:
17  |
18  |  __init__(self, cache_maxsize: int = 32, catalog: Optional[pathlib.Path] = None, jvm: Optional[jsaxonpy.jvm.JVM] = None, licensed_edition: bo
18 ol = False)
19  |      Initialize self.  See help(type(self)) for accurate signature.
20  |
21  |  transform(self, xml: Union[pathlib.Path, str], xsl: Union[pathlib.Path, str], params: Dict[str, str] = {}, pretty: bool = False) -> str
22  |
```