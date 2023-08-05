# algo
Set of tools for algorithmic trading

# Contributing 
To get started [install pipenv](https://pipenv.pypa.io/en/latest/install/#crude-installation-of-pipenv)

Install dependencies
```
pipenv install --dev
```

Active environment
```
pipenv shell
```

To use VSCode `Pyhton: Select Interpreter` and choose suggested PipEnv environment.


# Building And uploading
```sh
python -m build
twine upload ./dist/* --verbose
```


TODO: 
  * make `install_requires` dynamic based on Pipfile