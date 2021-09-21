.PHONY:
shell:  ## Load the deps and enter the virtualenvironment
	poetry shell

.PHONY:
python:  ## Run python console with deps (f.e. ptpython) loaded
	poetry run python

.PHONY:
pypi:  ## Open pypi package in browser
	xdg-open https://pypi.org/project/crackwifi

.PHONY:
publish:  ## Publish package to pypi
	poetry publish --build

.PHONY:
stats:  ## Open pypistats for the package in browser
	xdg-open https://pypistats.org/packages/crackwifi

.PHONY:
help:  ## Display this help screen
        @grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


