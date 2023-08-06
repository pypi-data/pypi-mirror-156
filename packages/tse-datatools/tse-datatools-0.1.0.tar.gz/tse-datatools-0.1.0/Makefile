.PHONY: clean

SOURCE_DIR = tse_datatools

init:
	pip install -r requirements.txt

clean: ## remove all build, test, coverage and Python artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .pytest_cache/
	rm -fr tse_datatools.egg-info/

lint: ## check style with flake8
	flake8

test: ## run tests quickly with the default Python
	py.test

coverage: ## check code coverage
	pytest --cov=$(SOURCE_DIR) tests/

install: clean ## install the package to the active Python's site-packages
	python setup.py install

build: ## build PyPI package
	python -m build .

publish: ## publish PyPI package
	twine upload dist/*
