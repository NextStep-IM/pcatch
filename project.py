import re
import mmap
import argparse
from sys import exit
from glob import iglob
from pathlib import Path
from typing import Generator, Pattern


def main():
    args = parse_cmd_args()

    for pat in args.PATTERN:
        args.PATTERN = str(pat)  # args.PATTERN is a list object

    pattern = handle_regex(args=args, pattern=args.PATTERN)

    for line in search_pattern(pattern, args.PATH):
        print(line)


def deploy_paths(file_paths: list) -> Generator:
    """Takes a path from expand_path() one by one and yields it to search_pattern()

    Args:
        file_paths (list): This is the list of paths given by the user. It is first taken as a param by search_pattern()

    Yields:
        Generator: Path object
    """
    # Filters paths with wildcards
    for arg in file_paths:
        for path in expand_path(arg):
            yield path


def expand_path(path) -> Generator:
    """Expands path with wildcards, leaves it as it was if there are no wildcards

    Args:
        path (str): A path with optional wildcards

    Yields:
        Generator: Path object
    """
    non_text_file_extensions = [
        # Binary Executables
        ".exe",
        ".dll",
        ".so",
        ".bin",
        ".elf",
        ".o",
        ".a",
        ".dylib",
        # Archives and Compressed Files
        ".zip",
        ".tar",
        ".gz",
        ".bz2",
        ".xz",
        ".7z",
        ".rar",
        ".iso",
        # Images
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tiff",
        ".ico",
        ".svg",
        # Audio
        ".mp3",
        ".wav",
        ".flac",
        ".aac",
        ".ogg",
        ".wma",
        ".m4a",
        # Video
        ".mp4",
        ".avi",
        ".mkv",
        ".mov",
        ".wmv",
        ".flv",
        ".mpeg",
        ".mpg",
        # Fonts
        ".ttf",
        ".otf",
        ".woff",
        ".woff2",
        ".eot",
        # Documents and Office Files
        ".pdf",
        ".doc",
        ".docx",
        ".ppt",
        ".pptx",
        ".xls",
        ".xlsx",
        ".odt",
        ".ods",
        ".odp",
        ".epub",
        # Database Files
        ".db",
        ".sqlite",
        ".accdb",
        ".mdb",
        ".sqlitedb",
        # System Files
        ".sys",
        ".dll",
        ".dmg",
        ".vmdk",
        ".iso",
        # Disk Images and Virtual Machines
        ".img",
        ".vhd",
        ".vdi",
        ".vmdk",
        # Binary Data Files
        ".dat",
        ".bin",
        ".dbf",
        # Object and Bytecode Files
        ".class",
        ".pyc",
        ".pyo",
        ".jar",
        ".war",
        # Encrypted Files
        ".gpg",
        ".aes",
        ".enc",
        # Application Files
        ".apk",
        ".ipa",
        ".msi",
        ".deb",
        ".rpm",
        # CAD and 3D Modeling
        ".dwg",
        ".dxf",
        ".stl",
        ".3ds",
        ".obj",
        # Configuration and System Backup
        ".bak",
        ".cfg",
        ".conf",
        ".ini",
        ".reg",
        ".log",
        # Multimedia Projects
        ".psd",
        ".ai",
        ".indd",
        ".prproj",
        ".aep",
        ".blend",
        # Temporary Files
        ".tmp",
        ".swp",
        ".lock",
        ".bak",
        # Miscellaneous
        ".crt",
        ".key",
        ".pem",
        ".cer",
    ]

    path = Path(path).expanduser()

    if path.is_dir():
        path = path / "**"

    p = str(path)  # iglob takes issue with PosixPath: It's not scriptable
    try:
        for expanded_path in iglob(p, recursive=True):
            path = Path(expanded_path)
            if path.is_file() and path.suffix not in non_text_file_extensions:
                yield path
    except PermissionError:
        pass


def parse_cmd_args():
    """Parses arguments given by user

    Returns:
        argparse.Namespace: Parsed user-given arguments
    """
    # Sets up the skeleton of the program

    parser = argparse.ArgumentParser(
        prog="pcat",
        description="Checks for given pattern in files",
        usage="python project.py [-h] [-w] [-i] PATTERN [PATH ...]",
    )

    # required param not allowed for positional args
    parser.add_argument(
        "PATTERN", type=str, help="Pattern to search for in file(s)", nargs=1
    )
    parser.add_argument(
        "PATH",
        nargs="*",
        default="**",
        help="Files(s) to search for. If no value is given, it will search the curreny working directory (non-recursively)",
    )
    parser.add_argument(
        "-w", "--word", action="store_true", dest="WORD", help="Search pattern as word"
    )
    parser.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        dest="NO_CASE",
        help="Search case-insensitively",
    )

    parsed_args = parser.parse_args()
    return parsed_args


def handle_regex(pattern: str, args) -> Pattern:
    """Generates the regex pattern according to options

    Args:
        pattern (str): Search pattern given by user
        args (argparse.Namespace): Parsed user-given arguments

    Returns:
        Pattern[bytes]: Generated pattern
    """
    try:
        # encode() converts string (args.PATTERN) to a bytes object
        compiled_pattern = re.compile(rb"" + pattern.encode(errors="strict") + rb"")
    except re.error as e:
        exit(f"pcat: regex error: {e}")

    if args.WORD:
        compiled_pattern = re.compile(rb"\b" + compiled_pattern.pattern + rb"\b")

    if args.NO_CASE:
        compiled_pattern = re.compile(
            rb"" + compiled_pattern.pattern + rb"", flags=re.IGNORECASE
        )

    return compiled_pattern


def search_pattern(pattern: Pattern[bytes], file_paths: list) -> list:
    """Searches pattern in file(s) with regex

    Args:
        pattern (Pattern[bytes]): Genereated regex pattern by handle_regex()
        file_paths (list): User-given paths

    Raises:
        ValueError: If file is empty. Reason: mmap.mmap() gives an error if file is empty

    Returns:
        list: Lines with matched pattern.
    """
    matches = []
    for file in deploy_paths(file_paths):
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
                        if match := re.findall(pattern, line):
                            if len(line) > 768:
                                line = line[0:767]
                            color_line = line
                            for pt in match:
                                color_pattern = b"\033[1;31m" + pt + b"\033[0;0m"
                                color_line = re.sub(pt, color_pattern, color_line)
                            try:
                                color_line = color_line.decode()
                            except UnicodeDecodeError:
                                continue
                            color_line_num = f"\033[0;32m{line_num}\033[0;0m"
                            if not matched_file:
                                color_path = (
                                    f"\033[0;34m{Path(file).absolute()}\033[0;0m"
                                )
                                matches.append(color_path)
                            matches.append(f"{color_line_num}:{color_line}")
                            matched_file = True

    return matches


if __name__ == "__main__":
    # import time
    # import cProfile
    # cProfile.run("main()")
    main()
