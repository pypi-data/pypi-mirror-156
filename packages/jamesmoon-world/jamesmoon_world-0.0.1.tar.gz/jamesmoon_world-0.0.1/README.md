# Hello World

This is an tutorial project demonstrating how to publish a python module to PyPI.

## Developing Hello World
To install helloworld, along with the tools you need to develop and run tests, run the following in your virtualenv:
```bash
$ pip install -e .
```

## Usage
```python
from helloworld import say_hello
# Generate "Hello, World!"
say_hello()

# Generate "Hello, James!"
say_hello("James")
```