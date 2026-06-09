import pathlib
import socket
import sys

import pytest

# Make agent/src importable when running pytest from agent/
_src = pathlib.Path(__file__).parent.parent / "src"
sys.path.insert(0, str(_src))
for _d in _src.iterdir():
    if _d.is_dir() and not _d.name.startswith("."):
        sys.path.insert(0, str(_d))

_FIXTURES = pathlib.Path(__file__).parent / "fixtures"


@pytest.fixture
def fixture_txt():
    return _FIXTURES / "sample.txt"


@pytest.fixture
def fixture_csv():
    return _FIXTURES / "sample.csv"


@pytest.fixture
def tmp_output(tmp_path):
    return tmp_path


def _corenlp_up():
    try:
        with socket.create_connection(("localhost", 9000), timeout=2):
            return True
    except OSError:
        return False


@pytest.fixture
def corenlp_running():
    if not _corenlp_up():
        pytest.skip("CoreNLP service not available on localhost:9000")
