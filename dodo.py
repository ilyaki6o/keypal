"""Automatization with doit."""

import glob
import os
from doit.task import clean_targets
from shutil import rmtree


def task_html():
    """Create docs html."""
    return {
        'actions': ['sphinx-build -M html ./docs/source ./keypal/docs/build'],
        'file_dep': glob.glob("./docs/source/*.rst") + glob.glob('keypal/*/*.py'),
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
            'python3 ./keypal/bitwarden/test_bitwarden_mocker.py',
        ],
    }


def task_test_client():
    """Run tests for client"""
    return {
        'actions': [
            'python3 ./keypal/bitwarden/test_bitwarden_client.py',
        ],
    }


def task_erase():
    """Delete all git untracked files (better to use then clean_targets)"""
    return {
            'actions': ['git clean -xdf'],
            }


'''def task_pot():
    """Re-create .pot."""
    return {
            'actions': ['p'],
            'file_dep': glob.glob(''),
            'targets': [''],
            'clean': True
           }


def task_po():
    """Update translations."""
    return {
            'actions': [
                ''
            ],
            'file_dep': [''],
            'targets': [''],
           }


def task_mo():
    """Compile translations."""
    return {
            'actions': [
                (os.makedirs, [""], {"exist_ok": True}),
                ''
            ],
            'file_dep': [''],
            'targets': [''],
            'clean': True
           }


def task_i18n():
    return {
            'actions': None,
            'task_dep': ['pot', 'po', 'mo'],
            'doc': 'task for generating translations',
            }



def task_sdist():
    return {
            'actions': ['python3 -m build -s -n'],
            'task_dep': ['erase'],
            'doc': 'generate source distribution',
            }


def task_wheel():
    return {
            'actions': ['python3 -m build -w'],
            'task_dep': ['i18n', 'html'],
            'doc': 'generate wheel',
            }
'''
