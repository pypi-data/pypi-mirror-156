# Python package for reading Application config file

## Installation

TODO

## How to use the library

TODO

## How to build it

### Prerequisities

``` shell
python -m pip install build twine
```

### Run the batch on win

- just run `build.bat` for publishing the version on testpypi or `build_prod.bat` for production pypi

### Run build only
Run it in the root folder

``` shell
python -m build
```

### How to bump the version

- See [How to Publish an Open-Source Python Package to PyPI | RealPython](https://realpython.com/pypi-publish-python-package/)
- [Documentation](https://pypi.org/project/bumpver/)
- Examples of how to run it (if you add `--dry`, it runs as dry run) 

``` shell
bumpver update --dry
bumpver update --patch --dry
bumpver update --minor --dry
bumpver update --major --dry
bumpver update --major --tag=beta --dry

```


#### Prerequsities

``` shell
python -m pip install bumpver
```


## How to install it for testing locally

Run it in the root folder

``` shell
pip install -e .
```

## How to test it

Run it in the `tests` folder

``` shell
python -m unittest
```

## Useful resources

- [How to upload your python package to PyPi | joelbarmettlerUZH](https://medium.com/@joel.barmettler/how-to-upload-your-python-package-to-pypi-65edc5fe9c56)
- [Packaging and distributing projects | python.org](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#configuring-your-project)
- [How to Publish an Open-Source Python Package to PyPI | RealPython](https://realpython.com/pypi-publish-python-package/)