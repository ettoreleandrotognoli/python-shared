PYTHON?=$(shell [ -f venv/bin/python ] && echo 'venv/bin/python' ||  echo 'python')
COVERAGE?=$(shell [ -f venv/bin/coverage ] && echo 'venv/bin/coverage' ||  echo 'coverage')

test:
	${PYTHON} -m unittest discover -t "src/" -s "src/tests/" -p "**.py"

coverage: clean
	${COVERAGE} run -a -m unittest discover -t "src/" -s "src/tests/" -p "**.py"
	${COVERAGE} html --include="pyshard/*,examples/*"

public:
	${PYTHON} setup.py register -r pypi
	${PYTHON} setup.py sdist upload -r pypi

public-test:
	${PYTHON} setup.py register -r pypitest
	${PYTHON} setup.py sdist upload -r pypitest

clean:
	rm -f $(shell find . -name "*.pyc")
	rm -rf htmlcov/ coverage.xml .coverage
	rm -rf dist/ build/
	rm -rf *.egg-info


