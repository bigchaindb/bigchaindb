.PHONY: check-deps help run test test-all coverage clean clean-build clean-pyc clean-test docs servedocs release dist install

.DEFAULT_GOAL := help


#############################
# Open a URL in the browser #
#############################
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT


##################################
# Display help for this makefile #
##################################
define PRINT_HELP_PYSCRIPT
import re, sys

print("BigchainDB 2.0 developer toolbox")
print("--------------------------------")
print("Usage:  make COMMAND")
print("")
print("Commands:")
for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("    %-16s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

##################
# Basic commands #
##################
DOCKER := docker
DC := docker-compose
BROWSER := python -c "$$BROWSER_PYSCRIPT"
HELP := python -c "$$PRINT_HELP_PYSCRIPT"
ECHO := /usr/bin/env echo

IS_DOCKER_COMPOSE_INSTALLED := $(shell command -v docker-compose 2> /dev/null)

################
# Main targets #
################

help: ## Show this help
	@$(HELP) < $(MAKEFILE_LIST)

run: check-deps ## Run BigchainDB from source (stop it with ctrl+c)
	@$(DC) up bigchaindb

start: check-deps ## Run BigchainDB from source and daemonize it (stop with `make stop`)
	@$(DC) up -d bigchaindb

stop: check-deps ## Stop BigchainDB
	@$(DC) stop

logs: check-deps ## Attach to the logs
	@$(DC) logs -f bigchaindb

test: check-deps ## Run all tests once
	@$(DC) run --rm bigchaindb pytest -v

test-watch: check-deps ## Run all tests and wait. Every time you change code, tests will be run again
	@$(DC) run --rm bigchaindb pytest -f -v

cov: check-deps ## Check code coverage and open the result in the browser
	@$(DC) run --rm bigchaindb pytest -v --cov=bigchaindb --cov-report html
	$(BROWSER) htmlcov/index.html

doc: ## Generate HTML documentation and open it in the browser
	@$(DC) run --rm --no-deps bdocs make -C docs/root html
	@$(DC) run --rm --no-deps bdocs make -C docs/server html
	$(BROWSER) docs/root/build/html/index.html

clean: clean-build clean-pyc clean-test ## Remove all build, test, coverage and Python artifacts
	@$(ECHO) "Cleaning was successful."

reset: check-deps ## Stop and REMOVE all containers. WARNING: you will LOSE all data stored in BigchainDB.
	@$(DC) down

###############
# Sub targets #
###############

check-deps:
ifndef IS_DOCKER_COMPOSE_INSTALLED
	@$(ECHO) "Error: docker-compose is not installed"
	@$(ECHO)
	@$(ECHO) "You need docker-compose to run this command. Check out the official docs on how to install it in your system:"
	@$(ECHO) "- https://docs.docker.com/compose/install/"
	@$(ECHO)
	@$(DC) # docker-compose is not installed, so we call it to generate an error and exit
endif

clean-build: # Remove build artifacts
	@rm -fr build/
	@rm -fr dist/
	@rm -fr .eggs/
	@find . -name '*.egg-info' -exec rm -fr {} +
	@find . -name '*.egg' -exec rm -f {} +

clean-pyc: # Remove Python file artifacts
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +

clean-test: # Remove test and coverage artifacts
	@rm -fr .tox/
	@rm -f .coverage
	@rm -fr htmlcov/
