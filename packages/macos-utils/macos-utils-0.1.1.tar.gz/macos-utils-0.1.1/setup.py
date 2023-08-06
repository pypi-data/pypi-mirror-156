# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['macos_utils']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['spotlight-exclude = '
                     'macos_utils.add_dir_to_spotlight_exclusions_list:main']}

setup_kwargs = {
    'name': 'macos-utils',
    'version': '0.1.1',
    'description': '',
    'long_description': '',
    'author': 'Teddy Xinyuan Chen',
    'author_email': '45612704+tddschn@users.noreply.github.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/tddschn/macos-utils',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
