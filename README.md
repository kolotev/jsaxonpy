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

Threads
-------
```
from concurrent.futures

xsl_file = '...'
worker_args = []

with ThreadPoolExecutor(max_workers=3) as executor:
for xml_file in ["file1.xml", "file2.xml", ..., "fileN.xml"]:
    worker_args.append((Path(xml_file), Path(xsl_file)))
    for out in executor.map(func, worker_args):
        assert out == xml
```

Processes
---------
```
from concurrent.futures import ProcessPoolExecutor

xsl_file = '...'
worker_args = []

with ProcessPoolExecutor(max_workers=3) as executor:
for xml_file in ["file1.xml", "file2.xml", ..., "fileN.xml"]:
    worker_args.append((Path(xml_file), Path(xsl_file)))
    for out in executor.map(func, worker_args):
        assert out == xml
```

Notes
=====

Supported and tested versions of Saxon are 9, 10, 11.

Before executing you application it is expected you set your java related
environment variables, including the `CLASSPATH` to point to your Java Saxon
installation.

You can use `JVM_OPTIONS` environment variable to set java virtual environment,
see example below.

```
export JVM_OPTIONS="-Xrs -Xmx3024m -XX:ActiveProcessorCount=24";
export CLASSPATH=/usr/local/Saxon-J/saxon-he-11.4.jar;
your_python_app.py
```
