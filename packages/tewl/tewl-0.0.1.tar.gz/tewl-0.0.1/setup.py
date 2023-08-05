# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['tewl']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'tewl',
    'version': '0.0.1',
    'description': 'Kewl tools for Python',
    'long_description': '# py-tewl\n\n[![Release](https://img.shields.io/github/v/release/kristjanvalur/py-tewl)](https://img.shields.io/github/v/release/kristjanvalur/py-tewl)\n[![Build status](https://img.shields.io/github/workflow/status/kristjanvalur/py-tewl/merge-to-main)](https://img.shields.io/github/workflow/status/kristjanvalur/py-tewl/merge-to-main)\n[![Commit activity](https://img.shields.io/github/commit-activity/m/kristjanvalur/py-tewl)](https://img.shields.io/github/commit-activity/m/kristjanvalur/py-tewl)\n[![Docs](https://img.shields.io/badge/docs-gh--pages-blue)](https://kristjanvalur.github.io/py-tewl/)\n[![Code style with black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Imports with isort](https://img.shields.io/badge/%20imports-isort-%231674b1)](https://pycqa.github.io/isort/)\n[![License](https://img.shields.io/github/license/kristjanvalur/py-tewl)](https://img.shields.io/github/license/kristjanvalur/py-tewl)\n\nKewl tools for Python\n\n- **Github repository**: <https://github.com/kristjanvalur/py-tewl/>\n- **Documentation** <https://kristjanvalur.github.io/py-tewl/>\n\n## Releasing a new version\n\n- Create an API Token on [Pypi](https://pypi.org/).\n- Add the API Token to your projects secrets with the name `PYPI_TOKEN` by visiting \n[this page](https://github.com/kristjanvalur/py-tewl/settings/secrets/actions/new).\n- Create a [new release](https://github.com/kristjanvalur/py-tewl/releases/new) on Github. \nCreate a new tag in the form ``*.*.*``.\n\nFor more details, see [here](https://fpgmaas.github.io/cookiecutter-poetry/releasing.html).\n\n---\n\nRepository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).',
    'author': 'Kristján Valur Jónsson',
    'author_email': 'fsweskman@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kristjanvalur/py-tewl',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
