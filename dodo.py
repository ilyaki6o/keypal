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
    """Run tests with mock."""
    return {
        'actions': [
            'python3 ./keypal/bitwarden/test_bitwarden_mocker.py',
        ],
    }


def task_test_client():
    """Run tests for client."""
    return {
        'actions': [
            'python3 ./keypal/bitwarden/test_bitwarden_client.py',
        ],
    }


def task_test_codestyle():
    return {
        'actions': [
            'flake8',
            'pydocstyle keypal',
        ],
    }


def task_erase():
    """Delete all git untracked files (better to use then clean_targets)."""
    return {
            'actions': ['git clean -xdf'],
           }


def task_pot():
    """Re-create .pot."""
    return {
            'actions': ['pybabel extract -o "./locales/tgbot.pot" -k _:2 keypal/tgbot'],
            'file_dep': glob.glob('keypal/tgbot/*.py'),
            'targets': ['./locales/tgbot.pot'],
            'clean': True
           }


def task_po():
    """Update translations."""
    return {
            'actions': [
                'pybabel update -D tgbot -d locales -i locales/tgbot.pot -l ru_RU.UTF-8'
            ],
            'file_dep': ['./locales/tgbot.pot'],
            'targets': ['./locales/ru_RU.UTF-8/LC_MESSAGES/tgbot.po'],
           }


def task_mo():
    """Compile translations."""
    return {
            'actions': [
                (os.makedirs, ["keypal/ru_RU.UTF-8/LC_MESSAGES"], {"exist_ok": True}),
                'pybabel compile -D tgbot -d keypal -l ru_RU.UTF-8 -i locales/ru_RU.UTF-8/LC_MESSAGES/tgbot.po'
            ],
            'file_dep': ['./locales/ru_RU.UTF-8/LC_MESSAGES/tgbot.po'],
            'targets': ['./keypal/ru_RU.UTF-8/LC_MESSAGES/tgbot.mo'],
            'clean': True
           }


def task_i18n():
    """Auto-creation locale."""
    return {
        'actions': None,
        'task_dep': ['pot', 'po', 'mo']
    }


def task_testall():
    return {
            'task_dep': ['test_client', 'test_mock', 'test_codestyle',],
            'actions': ['echo 0',]
            }


def task_sdist():
    return {
            'actions': ['python -m build -s -n'],
            'task_dep': ['erase'],
            'doc': 'generate source distribution',
            }


def task_wheel():
    return {
            'actions': ['python -m build -w'],
            'task_dep': ['i18n', 'html'],
            'doc': 'generate wheel',
            }
