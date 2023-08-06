# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['infosec_fools']

package_data = \
{'': ['*']}

install_requires = \
['rich>=12.4.4,<13.0.0', 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['infosec-fools = infosec_fools.main:app']}

setup_kwargs = {
    'name': 'infosec-fools',
    'version': '1.0.1',
    'description': 'Are you going to Hacker Summer Camp 2022?',
    'long_description': '# infosec-fools\n\n<p align="center">\n  <img width="500" height="500" src="https://raw.githubusercontent.com/daddycocoaman/infosec-fools/main/docs/logo.png">\n\n\nAre you going to Hacker Summer Camp, [you fools](https://twitter.com/kim_crawley/status/1539701262802878467)? It\'s a basic yes or no question.\n\n## Installation and Usage\n\n```\npipx install infosec-fools\ninfosec-fools\n```\n\n## Screenshots\n\n <img src="https://raw.githubusercontent.com/daddycocoaman/infosec-fools/main/docs/screenshot.png">\n\n\n</p>',
    'author': 'Leron Gray',
    'author_email': 'daddycocoaman@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
