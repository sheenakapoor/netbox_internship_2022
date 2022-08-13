#!/usr/bin/env python
# pylint: disable=C0103, E0401, R0913, R1720, R0914
# noqa: E501
"""This script parses XML file from command line."""

import sys
from bs4 import BeautifulSoup as Soup


def parser(file):
    """Parse XML and prints it in a pretty way."""
    with open(file, "r",  encoding="utf-8") as f:
        contents = f.read()
        feature = "lxml-xml"
        soup = Soup(contents, feature)
        print(soup.prettify())


if __name__ == "__main__":
    parser(sys.argv[1])
