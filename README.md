# Python Project Template

<p align="center">
<a href="https://github.com/ag-gipp/PythonProjectTemplate/actions/workflows/release.yml"><img alt="Actions Status" src="https://github.com/ag-gipp/PythonProjectTemplate/actions/workflows/release.yml/badge.svg">  
<a href="https://github.com/ag-gipp/PythonProjectTemplate/actions/workflows/main.yml"><img alt="Actions Status" src="https://github.com/ag-gipp/PythonProjectTemplate/actions/workflows/main.yml/badge.svg?branch=main">
<a href="https://github.com/ag-gipp/PythonProjectTemplate/blob/main/LICENSE"><img alt="License: MIT" src="https://black.readthedocs.io/en/stable/_static/license.svg"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

A simple starter for building well-maintainted python projects.
By Jan Philip Wahle.

## Features

- Unit testing
- Linting
- Type checker
- GitHub Actions
- Issue templates
- Releases
- Changelogs
- Documentation

## Getting Started

Create a new repository using this template by clicking ["Use this template"](https://github.com/ag-gipp/PythonProjectTemplate/generate)

Change the badges in the README.MD to the new project name

Clone your new repository and install the requirements in a virtual environment using pipenv.

```console
# Get the project code
git clone git@github.com:ag-gipp/{project_name}.git
cd {project_name}
# Install pipenv and dependencies
pip install pipenv
pipenv install --dev
```

You can also add new dependencies to the repository or remove ones you don't need.

```console
# Add dependency
pipenv add torch
# Add dev dependency
pipenv add pytest --dev
# Remove dependency
pipenv remove torch
```

## Running workflows

### CI

Whenever you create a pull request against the default branch, GitHub actions will create a CI job executing unit tests, linting and type checking.

### Local

To run these tests, linting, and type checks locally, install [act](https://github.com/nektos/act). With act you can run CI tests in docker containers the way they are run on GitHub actions.

To run the full check suite with act, execute:

```console
act -P self-hosted=nektos/act-environments-ubuntu:18.04 --reuse
```

The `--reuse` flag reuses the container so the subsequent runs are faster.
To run a single check like the Test from the pipeline, execute:

```console
act -j Test -P self-hosted=nektos/act-environments-ubuntu:18.04 --reuse
```

To run tests without docker locally, execute:

```console
pipenv run tests
```

However, it is recommended to run the main pipeline with act to make sure GitHub actions will produce the same results as you locally. If not, your won't be able to merge your changes.

## Linting and type checking

To run the linter (flake8) and check for typedefs (pyright), execute:

```console
act -j Linter -P self-hosted=nektos/act-environments-ubuntu:18.04 --reuse
act -j Typer -P self-hosted=nektos/act-environments-ubuntu:18.04 --reuse
```

You can also run this locally using:

```console
pipenv run linter
pipenv run typer
```

## Releases and deploys

New Git and GitHub releases as well as changelogs are automatically created and deployed when a pull request is merged into the default branch.
To indicate whether the PR is a patch, minor, or major update, please use #patch, #minor, #major in the last commit message of the PR and in the PR description.
Please refer to the Semantic Versioning [specification](https://semver.org/) for more information.

## Contributing

Fork the repo, make changes and send a PR. We'll review it together!

## License

This project is licensed under the terms of MIT license. Please see the LICENSE file for details.
