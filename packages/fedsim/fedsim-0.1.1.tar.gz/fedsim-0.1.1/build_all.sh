#!/bin/sh
# black --line-length 79 .
isort .
python setup.py bdist_wheel sdist

