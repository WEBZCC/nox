from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

GITHUB_FOLDER = Path(__file__).resolve().parent.parent / ".github"
sys.path.insert(0, str(GITHUB_FOLDER))
from action_helper import filter_version, setup_action  # noqa: E402

VALID_VERSIONS = {
    "2.7.18": "2.7",
    "3.9-dev": "3.9",
    "3.10": "3.10",
    "3.11": "3.11",
    "~3.12.0-0": "3.12",
    "pypy-3.7": "3.7",
    "pypy-3.8-v7.3.9": "3.8",
    "pypy-3.9": "3.9",
    "pypy3.10": "3.10",
}


@pytest.mark.parametrize("version", VALID_VERSIONS.keys())
def test_filter_version(version):
    assert filter_version(version) == VALID_VERSIONS[version]


def test_filter_version_invalid():
    with pytest.raises(ValueError, match=r"invalid version: 3"):
        filter_version("3")


def test_filter_version_invalid_major():
    with pytest.raises(ValueError, match=r"invalid major python version: x.0"):
        filter_version("x.0")


def test_filter_version_invalid_minor():
    with pytest.raises(ValueError, match=r"invalid minor python version: 3.x"):
        filter_version("3.x")


VALID_VERSION_LISTS = {
    "3.7, 3.8, 3.9, 3.10, 3.11, pypy-3.7, pypy-3.8, pypy-3.9": [
        "pypy-3.7",
        "pypy-3.8",
        "pypy-3.9",
        "3.7",
        "3.8",
        "3.9",
        "3.10",
        "3.11",
    ],
    "": ["3.11"],
    "~3.12.0-0": ["~3.12.0-0", "3.11"],
    "3.11.4": ["3.11.4"],
    "3.9-dev,pypy3.9-nightly": ["pypy3.9-nightly", "3.9-dev", "3.11"],
    "3.11, 3.10, 3.9, 3.8": ["3.10", "3.9", "3.8", "3.11"],
    ",".join(f"3.{minor}" for minor in range(20)): [
        f"3.{minor}"
        for i, minor in enumerate(minor_ for minor_ in range(20) if minor_ != 11)
    ] + ["3.11"],
}


@pytest.mark.parametrize("version_list", VALID_VERSION_LISTS.keys())
def test_setup_action(capsys, version_list):
    setup_action(version_list)
    captured = capsys.readouterr()
    lines = captured.out.splitlines()
    ordered_versions = VALID_VERSION_LISTS[version_list]
    assert lines == [f"interpreters={json.dumps(ordered_versions)}"]


def test_setup_action_multiple_pypy():
    with pytest.raises(
        ValueError,
        match=(
            r"multiple versions specified for the same 'major.minor' PyPy interpreter"
        ),
    ):
        setup_action("pypy3.9, pypy-3.9-v7.3.9")


def test_setup_action_multiple_cpython():
    with pytest.raises(
        ValueError,
        match=(
            r"multiple versions specified for the same 'major.minor' CPython"
            r" interpreter"
        ),
    ):
        setup_action("3.10, 3.10.4")
