import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

# To import scripts module we need to manipulate sys.path if not there
if str(Path.cwd()) not in sys.path:
    sys.path.insert(0, str(Path.cwd()))

import scripts.check_known_module_typos as ckmt
from scripts.check_known_module_typos import main

def test_main():
    with patch("scripts.check_known_module_typos.run_cli") as mock_run_cli:
        mock_run_cli.return_value = 42

        # Test main returns what run_cli returns
        assert main(["some", "args"]) == 42

        # Verify run_cli was called correctly
        mock_run_cli.assert_called_once()
        args, kwargs = mock_run_cli.call_args
        assert args[0] == "known-module-typos"

        # Verify the callback passed to run_cli works
        callback = args[1]
        with patch("scripts.check_known_module_typos.run_known_typos_check") as mock_run_check:
            callback()
            mock_run_check.assert_called_once_with(ckmt.REPO_ROOT)
