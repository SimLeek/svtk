# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


import os.path

readme = ""
here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, "README.rst")
if os.path.exists(readme_path):
    with open(readme_path, "rb") as stream:
        readme = stream.read().decode("utf8")


setup(
    long_description=readme,
    name="svtk",
    version="0.2.0",
    description="Streaming addons for VTK",
    python_requires="==3.*,>=3.6.0",
    project_urls={"repository": "https://github.com/simleek/displayarray"},
    author="SimLeek",
    author_email="simulator.leek@gmail.com",
    license="MIT",
    entry_points={"console_scripts": ["displayarray = displayarray.__main__:main"]},
    packages=[
        "svtk",
        "svtk.lib",
        "svtk.vtk_classes",
    ],
    package_dir={"": "."},
    package_data={},
    install_requires=[
        "vtk",
        "numpy",
    ],
    extras_require={
        "dev": ["black", "tox", "coverage", "pytest", "pydocstyle", "mypy"],
    },
)
