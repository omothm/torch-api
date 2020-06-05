"""Torch Test Package

This is where all tests of the Torch API reside. Run

    python -m tests help

for instructions on how to use.
"""

__author__ = "Omar Othman <omar.othman@live.com>"


import pkgutil
import sys
import importlib
import inspect


EXCLUDED_MODULES = ["__main__"]


def main():
    if len(sys.argv) == 1:
        print("A command must be provided\n")
        _print_help()
        return

    # Get the names of all modules in this package
    all_modules = [name for _, name, _ in pkgutil.iter_modules(
        [__package__]) if name not in EXCLUDED_MODULES]

    command = sys.argv[1]

    if command == "help":
        _print_help()
        return
    if command == "list":
        _print_module_list(all_modules)
        return
    if command == "modules":
        if len(sys.argv) == 2:
            print("Module names must be provided\n")
            _print_help()
            return
        modules = sys.argv[2:]
    elif command == "all":
        modules = all_modules
    else:
        print(f"Unknown command '{command}'\n")
        _print_help()
        return

    print("Torch Test Package")
    print("==================")
    for i, module in enumerate(modules):
        title = f"Module {i + 1} of {len(modules)} - {module}"
        print(f"\n{title}")
        print("-" * len(title))
        module_funcs = importlib.import_module(f"{__package__}.{module}")
        main_func = [value for _, value in inspect.getmembers(
            module_funcs, lambda x: hasattr(x, "__name__") and x.__name__ == "main")]
        if not main_func:
            print("Error: Test module does not contain a main() function")
        else:
            main_func = main_func[0]
            try:
                main_func()
            except Exception as e:
                print(f"An error occurred while running '{module}'")
                print(str(e))


def _print_module_list(all_modules):
    print("Available modules:")
    for module in all_modules:
        print(f"  {module}")


def _print_help():
    prefix = f"python -m {__package__}"
    print(f"usage 1: {prefix} all")
    print("    Runs all tests")
    print(f"usage 2: {prefix} list")
    print("    Lists all test modules")
    print(f"usage 3: {prefix} modules <modules>")
    print("    Runs test for the specific module(s) separated by spaces")
    print(f"usage 4: {prefix} help")
    print("    Prints this help message")


if __name__ == "__main__":
    main()
