# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pretext_cli_redirect']

package_data = \
{'': ['*']}

install_requires = \
['pretextbook']

setup_kwargs = {
    'name': 'pretext-cli',
    'version': '0.1.0',
    'description': 'Requires pretextbook package (the PreTeXt CLI)',
    'long_description': None,
    'author': 'Steven Clontz',
    'author_email': 'steven.clontz@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.5,<4.0.0',
}


setup(**setup_kwargs)
