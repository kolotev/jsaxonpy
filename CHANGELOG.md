# Changelog

All notable changes to this project will be documented in this file.

## [0.7.2] 2023-01-30

### Updated

- an alternative implementation of workaround for issue
  (#345)[(https://github.com/kivy/pyjnius/issues/345)] was made in replacement
  of using threading.Lock().


## [0.7.1] 2023-01-29

### Fixed

- exceptions caused by presumably thread unsafe code of pyjnius were fixed with
  threading.Lock() mechanism.


## [0.7.0] 2023-01-28

### Added

- optimizations for reuse of earlier created instances of transformer were made;

### Fixed

- jvm.py: a failure with missing env variable `JVM_OPTIONS` was fixed;
- workaround for JVM exception: Invalid JSON input on line 1: An empty string
  is not valid JSON net.sf.saxon.s9api.SaxonApiException was implemented;
- spelling typo for singleton (file signleton.py) was fixed;


## [0.6.0] 2022-12-15

### Added

- support for catalog file was implemented (Saxon >= 11);


## [0.5.0] 2022-12-14

### Added

- makefile was added;

### Fixed

- xslt.py: Fixed the issue with _stream_source() method;
- tox.ini: issue with failing tox in parallel mode (`-p auto`) was fixed with
  better isolation of environments;
- unnecessary print() statements were removed;


## [0.4.3] 2022-11-22

- Initial release
