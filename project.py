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
    args = parse_args()
    path_list: list[Path] = [Path(arg) for arg in args.FILENAME]

    # encode() converts string (args.pattern) to a bytes object
    pattern = re.compile(rb"" + args.PATTERN.encode(errors="strict") + rb"")

    for line in search_pattern(pattern, path_list):
        print(line)


def parse_args():
    # Sets up the skeleton of the program

    parser = argparse.ArgumentParser(
        prog="pcat",
        description="Checks for given pattern in files",
    )

    # required param not allowed for positional args
    parser.add_argument(
        "PATTERN", type=str, help="Pattern to search for in file(s)", nargs=1
    )

    # TODO: Allow wildcards
    parser.add_argument("FILENAME", nargs="*", default="*")

    parsed_args = parser.parse_args()
    return parsed_args


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
                            color_pattern = (
                                Colors.RED + match.group().decode() + Colors.RESET
                            )
                            color_path = (
                                Colors.BLUE + str(file.absolute()) + Colors.RESET
                            )
                            color_line = re.sub(pattern, color_pattern.encode(), line)
                            color_line_num = Colors.GREEN + str(line_num) + Colors.RESET

                            matches.append(
                                f"{color_path}\n{color_line_num}:{color_line.decode()}"
                            )

    return matches


if __name__ == "__main__":
    main()
