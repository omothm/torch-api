"""Converts jpg files to base64.

This script accepts args.

Synopsis:

    convert.py [<input_path>] [<output_dir>]

<input_path>: optional path to an input file or dir. If not provided, the local
              data/jpg directory is used.

<output_dir>: optional output directory. This must be a directory, not a file.
              If not provided, the local data/base64 is used.

Note: Direct parent of each file is considered its "class".
"""


__author__ = "Omar Othman <omar.othman@live.com>"


import base64
import os
from pathlib import Path
import sys
from tqdm import tqdm


INPUT_DIR = os.path.join(os.path.dirname(__file__), "data", "jpg")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data", "base64")


def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else INPUT_DIR
    output_dir = sys.argv[2] if len(sys.argv) > 2 else OUTPUT_DIR

    # get files
    input_filenames = {}
    all_filenames = []
    if os.path.isdir(input_path):
        for dirpath, _, filenames in os.walk(input_path):
            for filename in filenames:
                all_filenames.append(os.path.join(dirpath, filename))
    else:
        all_filenames.append(input_path)
    if not all_filenames:
        print("error: no files found")
        sys.exit(1)
    for filename in all_filenames:
        fileclass = os.path.basename(os.path.dirname(filename))
        if fileclass not in input_filenames:
            input_filenames[fileclass] = []
        input_filenames[fileclass].append(filename)

    # convert
    for fileclass, filenames in input_filenames.items():
        for filename in tqdm(filenames, desc=fileclass, unit="file"):
            basename = os.path.splitext(os.path.basename(filename))[0]
            output_filename = os.path.join(
                output_dir, fileclass, basename + ".txt")
            # ensure the output path exists
            Path(os.path.dirname(output_filename)).mkdir(
                parents=True, exist_ok=True)
            convert(filename, output_filename)


def convert(jpg_filename, base64_filename):
    """Converts `jpg_filename` jpeg file into a base64 txt file and saves it as
    `base64_filename`.
    """
    # read jpg file
    with open(jpg_filename, "rb") as jpg_file:
        jpg_bytes = jpg_file.read()
    # convert
    base64_string = base64.b64encode(jpg_bytes).decode('utf-8')
    # save base64 txt file
    with open(base64_filename, "w") as base64_file:
        base64_file.write("data:image/jpeg;base64,")
        base64_file.write(base64_string)


if __name__ == "__main__":
    main()
