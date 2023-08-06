 #!/usr/bin/env python
###############################################################################

###############################################################################

from setuptools import setup, find_packages

setup(
    name="sinais",
    version="0.0.1",
    description="Generate signals for signal processing quite easily using python.",
    author="Rafael do Nascimento Pereira",
    author_email="rnp@25ghz.net",
    url="https://github.com/rafaelnp/sinais",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(where="sinais"),

    python_requires=">=3.8",

    install_requires = [
        "fxpmath>=0.4.0",
        "numpy>=1.20.0",
        "plotly>=5.1.0",
    ],
    extras_requires = [
        "pytest==6.2.4",
    ],
    py_modules=["sinais"],
)
