"""etl-ohlcv CLI."""

from __future__ import annotations

import setuptools


DOCLINES = __doc__.split("\n")


def get_requirements() -> list[str]:
    with open("requirements/base.txt", "r") as fp:
        package_list = fp.readlines()
        package_list = [package.rstrip() for package in package_list]

    return package_list


setuptools.setup(
    name="etl.ohlcv",
    description=DOCLINES[0],
    author="Quantitative Developers",
    version="0.2.0",
    install_requires=get_requirements(),
    packages=setuptools.find_namespace_packages(
        include=[
            "etl.*",
        ]
    ),
    python_requires=">=3.7",
)
