import re
import mmap
import argparse
from glob import escape, iglob
from pathlib import Path
from typing import Generator, Pattern


class Colors:
    RED = "\033[1;31m"
    GREEN = "\033[0;32m"
    BLUE = "\033[34m"
    RESET = "\033[0;0m"


def main():
    args = parse_cmd_args()

    for pat in args.PATTERN:
        args.PATTERN = str(pat)
    # encode() converts string (args.pattern) to a bytes object
    pattern = re.compile(rb"" + args.PATTERN.encode(errors="strict") + rb"")

    for line in search_pattern(pattern, args.FILENAME):
        print(line)


def filter_paths(file_paths) -> Generator:
    path_list: list[Path] = []
    wildcard_paths = []

    # Filters paths with wildcards
    for arg in file_paths:
        if glob.escape(arg) == arg:
            path_list.append(Path(arg).expanduser())
        else:
            wildcard_paths.append(arg)

    if wildcard_paths:
        for p in wildcard_paths:
            for path in expand_path(p):
                yield path
    if path_list:
        for path in path_list:
            yield path


def expand_path(wildcard_path) -> Generator:
    # See: https://stackoverflow.com/a/51108375/23356858
    p = str(Path(wildcard_path).expanduser())
    try:
        for path in iglob(p, recursive=True):
            path = Path(path)
            if path.is_file():
                yield path
    except PermissionError:
        pass


def parse_cmd_args():
    # Sets up the skeleton of the program

    parser = argparse.ArgumentParser(
        prog="pcat",
        description="Checks for given pattern in files",
    )

    # required param not allowed for positional args
    parser.add_argument(
        "PATTERN", type=str, help="Pattern to search for in file(s)", nargs=1
    )
    parser.add_argument("FILENAME", nargs="*", default="**")

    parsed_args = parser.parse_args()
    return parsed_args


def search_pattern(pattern: Pattern[bytes], file_paths: list) -> list:
    matches = []
    for file in filter_paths(file_paths):
        try:
            if file.stat().st_size == 0:  # Check if file is empty
                raise ValueError
            file_obj = open(file, "r")
        except OSError as oe:
            print(f"pcat: {file}: {oe}")
            continue
        except ValueError:
            continue
        else:
            with file_obj:
                with mmap.mmap(
                    file_obj.fileno(), length=0, access=mmap.ACCESS_READ
                ) as mmap_obj:  # Raises ValueError if file is empty
                    matched_file = False
                    for line_num, line in enumerate(iter(mmap_obj.readline, b"")):
                        if match := re.search(pattern, line):
                            # decode() converts byte object to string
                            color_pattern = (
                                Colors.RED + match.group().decode() + Colors.RESET
                            )
                            color_line = re.sub(pattern, color_pattern.encode(), line)
                            color_line_num = Colors.GREEN + str(line_num) + Colors.RESET
                            if not matched_file:
                                color_path = (
                                    Colors.BLUE + str(file.absolute()) + Colors.RESET
                                )
                                matches.append(color_path)
                            color_line = color_line.decode(
                                "latin-1"
                            )  # "latin-1" fixes UnicodeDecodeError. See: Issue #1
                            matches.append(f"{color_line_num}:{color_line}")
                            matched_file = True

    return matches


if __name__ == "__main__":
    main()
