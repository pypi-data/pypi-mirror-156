# Example Package
### To build the package
    python -m pip install --upgrade build
    python -m build

### To upload the package 
    python -m pip install --upgrade twine
    python -m twine upload --repository pypi dist/*
### To install the local version package 
    python setup.py install