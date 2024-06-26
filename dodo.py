"""Doit autogeneration."""


import glob 
from doit.task import clean_targets
from shutil import rmtree
import os



def task_html():
    """Crete docs html."""
    return {
        'actions': ['sphinx-build -M html ./docs/source ./keypal/docs/build'],
        'file_dep': glob.glob("./docs/source/*.rst"),
        'targets': ['./keypal/docs/build'],
        'clean': [clean_build, clean_targets],
    }


def clean_build():
    """Remove docs generates."""
    if os.path.exists('./keypal/docs/build'):
        rmtree("./keypal/docs/build")


def task_test_mock():
    """Run tests with mock"""
    return {
        'actions': [
            'python3  ./keypal/bitwarden/test_bitwarden_mocker.py',
        ],
    }


def task_test_client():
    """Run tests with mock"""
    return {
        'actions': [
            'python3  ./keypal/bitwarden/test_bitwarden_client.py',
        ],
    }

