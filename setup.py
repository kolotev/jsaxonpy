from setuptools import setup

setup(
    name="jsaxonpy",
    maintainer="Andrei Kolotev",
    maintainer_email="kolotev@ncbi.nlm.nih.gov",
    setup_requires=[
        "setuptools_scm[toml]>=6.2",
        "tox-setuptools",
    ],
    tests_require=["tox>=3.3,<4"],
)
