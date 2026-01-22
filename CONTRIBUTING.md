# Contribution Guide

## Bug Reports

For bug reports [submit an issue](https://github.com/PilotDataPlatform/common/issues).

## Pull Requests

1. Fork the [main repository](https://github.com/PilotDataPlatform/common).
2. Create a feature branch to hold your changes.
3. Work on the changes in your feature branch.
4. Add [Unit Tests](#unit-tests).
5. Follow the [Getting Started](README.md) instructions to set up the package.
6. Test the code and create a pull request.

### Unit Tests

When adding a new feature or fixing a bug, unit tests are necessary to write. We use Pytest as our testing framework and all test cases are written under the `tests` directory.

Run test cases with Poetry and Pytest:
```
poetry run pytest
```

### Integrating Package Locally

Occasionally, it may be necessary to generate a local common package in order to test its integration with other services.

1. Generate a `.whl` file of the common package:
```
pip install wheel twine
python3 setup.py sdist bdist_wheel
```
2. Install the resulting `.whl` file into your desired service (see the [Getting Started](README.md) instructions).
