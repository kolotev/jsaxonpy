from setuptools import setup

setup(
    setup_requires=[
        "setuptools_scm[toml]>=6.2",
        "tox-setuptools",
    ],
    tests_require=["tox>=3.3,<4"],
)
