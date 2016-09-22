APP = freddist

.PHONY: default test isort check-isort check-flake8 check-all

default: check-all

test:
	python -m unittest discover

isort:
	isort --recursive ${APP}

check-all: check-isort check-flake8

check-isort:
	isort --recursive --check-only --diff ${APP}

check-flake8:
	flake8 --config=.flake8 --format=pylint --show-source ${APP}
