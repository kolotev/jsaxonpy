PYTHON_VERSION = 3.9
PYTHONNOUSERSITE = /dev/null
PIPENV := $(shell which pipenv 2>/dev/null)
REBUILD_FLAG := ""

all:
	@echo "Run 'make publish_testpypi' or 'make publish' or check/read makefile"

init:
	@: $(PIPENV) --rm 2>/dev/null || echo ""
	$(PIPENV) --python $(PYTHON_VERSION)

pip_install:
	source $(shell ${PIPENV} --venv)/bin/activate && pip install .[test,dev]

build: clean init pip_install
	source $(shell ${PIPENV} --venv)/bin/activate && python3 -m build

publish_test: build
	source $(shell ${PIPENV} --venv)/bin/activate && python3 -m twine upload --repository testpypi dist/*

publish: build
	source $(shell ${PIPENV} --venv)/bin/activate && python3 -m twine upload --repository pypi dist/*

test: tox.ini
	tox -p auto $(REBUILD_FLAG)

tox.ini: pyproject.toml
	$(eval REBUILD_FLAG := --recreate)
	touch tox.ini

clean:
	rm -rf dist build *.whl
