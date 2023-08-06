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
    'version': '1.0.0',
    'description': 'Are you going to Hacker Summer Camp 2022?',
    'long_description': '# infosec-fools\nAre you going to Hacker Summer Camp, [you fools](https://twitter.com/kim_crawley/status/1539701262802878467)?\n\n`pipx install infosec-fools`\n',
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
