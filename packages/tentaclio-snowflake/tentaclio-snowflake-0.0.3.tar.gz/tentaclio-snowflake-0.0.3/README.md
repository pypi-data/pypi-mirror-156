
# tentaclio-snowflake

A package containing all the dependencies for the snowflake tentaclio schema .

## Quick Start

This project comes with a `Makefile` which is ready to do basic common tasks

```
$ make help
install                       Initalise the virtual env installing deps
clean                         Remove all the unwanted clutter
lock                          Lock dependencies
update                        Update dependencies (whole tree)
sync                          Install dependencies as per the lock file
lint                          Lint files with flake and mypy
format                        Run black and isort
test                          Run unit tests
circleci                      Validate circleci configuration (needs circleci cli)
```

## Configuring access to Snowflake

Your connection url should be in the following format:

```
snowflake://<username>:<password>@<host>
```