import pytest
from unittest.mock import patch
from project import parse_cmd_args
import sys
import tempfile  # for creating temporary files and dirs
from binaryornot.check import is_binary


def test_parse_args():
    test_args = ["pcat", "lorem", "file1.txt", "file2.txt"]
    with patch.object(sys, "argv", test_args):
        args = parse_cmd_args()
        assert args.PATTERN == ["lorem"]  # Type is list because of nargs=1
        assert args.FILENAME == ["file1.txt", "file2.txt"]
    test_args = ["pcat"]
    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit):
            parse_cmd_args()
