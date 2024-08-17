import re
import sys
import pytest
from pathlib import Path
from shutil import rmtree
from unittest.mock import patch
from tempfile import gettempdir  # for creating temporary files and dirs
from project import parse_cmd_args, deploy_paths, search_pattern


def test_parse_cmd_args():
    test_args = ["pcat", "lorem", "file1.txt", "file2.txt"]
    with patch.object(sys, "argv", test_args):
        args = parse_cmd_args()
        assert args.PATTERN == ["lorem"]  # Type is list because of nargs=1
        assert args.FILENAME == ["file1.txt", "file2.txt"]
        assert args.WORD == False
        assert args.NO_CASE == False
    test_args = ["pcat"]
    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit):
            parse_cmd_args()
    test_args = ["pcat", "-w", "-i", "lorem", "file1.txt"]
    with patch.object(sys, "argv", test_args):
        args = parse_cmd_args()
        assert args.WORD == True
        assert args.NO_CASE == True
    test_args = ["pcat", "-wi", "lorem"]
    with patch.object(sys, "argv", test_args):
        args = parse_cmd_args()
        assert args.WORD == True
        assert args.NO_CASE == True


def helper_func():
    tmp_loc = Path(gettempdir())
    temp_dir = tmp_loc / "test_dir"
    Path.mkdir(temp_dir, exist_ok=True)
    file1 = temp_dir / "file1.txt"
    file2 = temp_dir / "file2.cpp"
    sub_dir = temp_dir / "sub_dir"
    Path.touch(file1)
    Path.touch(file2)
    Path.mkdir(sub_dir, exist_ok=True)
    return [temp_dir, file1, file2]

def test_deploy_paths():
    temp_dir, file1, file2 = helper_func()
    assert list(deploy_paths([temp_dir])) == [file1, file2]
    assert list(deploy_paths([f"{temp_dir}/**"])) == [file1, file2]
    assert list(deploy_paths([f"{temp_dir}/file1*", f"{temp_dir}/*.cpp"])) == [file1, file2]
    rmtree(temp_dir)


def test_search_pattern():
    temp_dir, file1, file2 = helper_func()
    with open(file1, "w") as f1, open(file2, "w") as f2:
        f1.write("Lorem lorem ipsum ip\n")
        f2.write(r"#include <iostream>\n\nint main() \{\n\tcout << \"hello, world\";\n\treturn 0\n\}")
    pattern =  re.compile(rb"" + b"Lorem" + rb"")
    assert len(search_pattern(pattern=pattern, file_paths=[temp_dir])) != 0
    pattern = re.compile(rb"" + b"<iostream>" + rb"") 
    assert len(search_pattern(pattern=pattern, file_paths=[temp_dir])) != 0
    pattern = re.compile(rb"" + b"hello" + rb"")
    assert len(search_pattern(pattern=pattern, file_paths=[f"{temp_dir}/file1.txt"])) == 0     
    rmtree(temp_dir)