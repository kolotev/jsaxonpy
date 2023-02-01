PYTHONNOUSERSITE = /dev/null
SETUP_PY_PYTHON ?= python3.9
PYTHON_VERSION := $(shell ${SETUP_PY_PYTHON} -c 'import sys; print("{0}.{1}".format(*sys.version_info[:2]))')
VENV ?= $(or $(shell pipenv --venv 2>/dev/null), .venv)

CONF_FILES = makefile pyproject.toml tox.ini setup.py
SRC_FILES = $(shell ls src/**/*.py | grep -v src/jsaxonpy/_version.py)
TESTS_FILES = $(shell ls tests/*.py)

REBUILD_FLAG =

.ONESHELL:

all:
	@echo "Run 'make publish_pypi_test' or 'make publish_pypi' " \
		"or check/read makefile for other rules."


${VENV}/bin/activate: pyproject.toml
	@echo -n "Checking python virtual environment ... "
	$(eval VENV_EXISTS := $(shell test -e ${VENV}/bin/activate && echo yes || echo no))
	if [[ $(VENV_EXISTS) = "no" ]]; then echo "missing."; \
	 	echo -n "Creating new python virtual environment ... "; \
		pipenv --python ${PYTHON_VERSION} 2>/dev/null || ${SETUP_PY_PYTHON} -m venv "${VENV}"; \
		echo "done"
	else \
		echo "installed."; \
	fi && touch $@


activate: ${VENV}/bin/activate
	@$(eval VENV := $(or $(shell pipenv --venv 2>/dev/null), ${VENV}))
	@test -x "${VENV}/bin/activate" || chmod +x "${VENV}/bin/activate"
	@echo -n "Activating python virtual environment from ${VENV}/bin/activate ... "
	@source ${VENV}/bin/activate && echo "done" && touch $@


install: $(CONF_FILES) activate
	@echo "Installing python packages ..."
	@source ${VENV}/bin/activate
	@rm -rf build
	pip install .[test,dev] && touch $@


test: tests


tests: $(SRC_FILES) $(TESTS_FILES) install
	@echo "Starting tests ..."
	@source ${VENV}/bin/activate
	tox -p auto $(REBUILD_FLAG) && touch $@


build: tests
	@echo "Building package ..."
	@source ${VENV}/bin/activate
	@rm -rf build dist
	${SETUP_PY_PYTHON} -m build && touch $@


tox.ini: pyproject.toml
	@$(eval REBUILD_FLAG := --recreate)
	@touch $@


publish_pypi_test: build
	@source ${VENV}/bin/activate
	${SETUP_PY_PYTHON} -m twine upload --repository testpypi dist/*


publish_pypi: build
	@source ${VENV}/bin/activate
	${SETUP_PY_PYTHON} -m twine upload --repository pypi dist/*


clean:
	@echo "Cleaning ..."
	rm -rf dist build *.whl


destroy: clean
	@echo "Destroyng venv related assets ..."
	pipenv --rm 2>/dev/null;
	rm -rf ${VENV} Pipfile install activate
