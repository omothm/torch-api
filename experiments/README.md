# Torch API Experiments

To run a script inside this directory, run it as a module **from the project's root directory** of the project to be able to access the API. For example, while in the root directory, run:

    $ python -m experiments.bg_threshold.bg_performance

(See [mod.py](..\mod.py) for an easier way write out module names.)

## Environment Issues

If your VS Code linter is having difficulties with upper-level imports (from `torchapi/`), add a file named `.env` to the project's root directory, with this content

    PYTHON_PATH=<PATH_TO_PROJECT>

where `<PATH_TO_PROJECT>` is the absolute system path to the project's root directory (i.e. where `.env` itself exists). You may need to restart VS Code afterwards.
