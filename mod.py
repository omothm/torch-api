"""Module runner

A shortcut to run a module by referencing its file (for leveraging
autocomplete). For example,

    python mod.py parent\\dir\\file.py [args]

becomes

    python -m parent.dir.file [args]
"""

__author__ = "Omar Othman <omar.othman@live.com>"


import subprocess
import sys


def main():
    if len(sys.argv) == 1:
        print("Quickly run a module by referencing the python file. For example,")
        print("    python mod.py parent\\dir\\file.py [args]")
        print("becomes")
        print("    python -m parent.dir.file [args]")
        sys.exit(0)
    module = sys.argv[1]
    # remove ".py"
    module = module[:-3]
    module = module.replace("\\", ".")
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    subprocess.run(["python", "-m", module, *args], check=False)


if __name__ == "__main__":
    main()
