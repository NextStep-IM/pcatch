import argparse
from pathlib import Path
import re
import mmap


class Colors:
    RED = "\033[1;31m"
    GREEN = "\033[0;32m"
    BLUE = "\033[34m"
    RESET = "\033[0;0m"


def main():
    pattern, path_list = parse_args()
    for line in search_pattern(pattern, path_list):
        print(line)


def parse_args():
    # Sets up the skeleton of the program

    parser = argparse.ArgumentParser(
        prog="pcat",
        description="Checks for given pattern in files",
    )

    # required param not allowed for positional args
    parser.add_argument("PATTERN", type=str, help="Pattern to search for in file(s)")

    # TODO: Allow wildcards
    parser.add_argument("FILENAME", nargs="*", default="*")

    args = parser.parse_args()
    path_list = [Path(arg) for arg in args.FILENAME]

    # encode() converts string (args.pattern) to a bytes object
    pattern = re.compile(rb"" + args.PATTERN.encode(errors="strict") + rb"")

    return [pattern, path_list]


def search_pattern(pattern: re, file_path: list[Path]) -> list:
    matches = []
    for file in file_path:
        try:
            file_obj = open(file, "r")
        except OSError as oe:
            print(f"pcat: {file}: {oe}")
            break
        else:
            with file_obj:
                with mmap.mmap(
                    file_obj.fileno(), length=0, access=mmap.ACCESS_READ
                ) as mmap_obj:
                    for line_num, line in enumerate(iter(mmap_obj.readline, b"")):
                        if match := re.search(pattern, line):
                            # decode() converts byte object to string
                            colored_str = Colors.RED + match.group().decode() + Colors.RESET
                            line = re.sub(pattern, colored_str.encode(), line)
                            matches.append(
                                f"{Colors.GREEN}{line_num}{Colors.RESET}:{line.decode()}"
                            )

    return matches


if __name__ == "__main__":
    main()
