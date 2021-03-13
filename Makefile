.PHONY: clean lint test

help:
	@echo "  env         install all dependencies"
	@echo "  clean       remove unwanted stuff"
	@echo "  lint        check style with black"
	@echo "  test        run tests"
	@echo "  cov-term    run coverage output term"
	@echo "  bump-minor  update version 0.1.0 to 0.2.0"
	@echo "  bump-patch  update version 0.1.0 to 0.1.1"

env:
	pip install --upgrade pip
	pip install poetry
	poetry install

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .pytest_cache
	rm -f .coverage
	rm -fr htmlcov/

cov-term: clean-pyc
	pytest -s --cov=pytwitter --cov-report term

cov-html: clean-pyc
	pytest -s --cov=pytwitter --cov-report html

lint:
	black .

lint-check:
	black --check .

test:
	pytest -s

bump-minor:
	bump2version minor

bump-patch:
	bump2version patch