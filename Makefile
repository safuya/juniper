.PHONY: all install-dev test coverage cov test-all tox docs release clean-pyc

all: test

install-dev:
	pip install -q -e .[venv3]
	pip install -r requirements/dev.txt

test: clean-pyc
	python -m pytest --cov .

coverage: clean-pyc install-dev
	coverage run -m pytest
	coverage report
	coverage html

cov: coverage

test-all: install-dev
	tox

tox: test-all

docs: clean-pyc
	$(MAKE) -C docs html

gh-pages:
	git checkout gh-pages
	rm -rf _images _sources _static
	git checkout feature/add-sphinx
	$(MAKE) -C docs html
	mv -fv docs/_build/html/* ./
	rm -rf assets docs examples juniper requirements scripts tests
	git add -A
	git commit -m "Generated gh-pages for `git log master -1 --pretty=short --abbrev-commit`" && git push origin gh-pages; git checkout feature/add-sphinx



release:
	python scripts/make-release.py

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +