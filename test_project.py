import pytest
from unittest.mock import patch
from project import parse_args
import sys
import tempfile # for creating temporary files and dirs

def test_parse_args():
    test_args = ["pcat", "lorem", "file1.txt", "file2.txt"]
    with patch.object(sys, "argv", test_args):
        args = parse_args()
        assert args.PATTERN == ["lorem"] # Type is list because of nargs=1
        assert args.FILENAME == ["file1.txt", "file2.txt"]
