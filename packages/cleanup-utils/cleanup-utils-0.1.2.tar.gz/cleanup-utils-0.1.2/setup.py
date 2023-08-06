# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cleanup_utils']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0']

entry_points = \
{'console_scripts': ['mac_clean_library_cache = '
                     'cleanup_utils.mac_clean_library_cache:main',
                     'macclc = cleanup_utils.mac_clean_library_cache:main']}

setup_kwargs = {
    'name': 'cleanup-utils',
    'version': '0.1.2',
    'description': 'Utility scripts to clean up your system',
    'long_description': '',
    'author': 'Teddy Xinyuan Chen',
    'author_email': '45612704+tddschn@users.noreply.github.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/tddschn/cleanup-utils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
