# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['miqro']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'paho-mqtt>=1.6.1,<2.0.0']

setup_kwargs = {
    'name': 'miqro',
    'version': '1.0.0',
    'description': 'MIQRO is an MQTT Micro-Service Library for Python',
    'long_description': None,
    'author': 'Daniel Fett',
    'author_email': 'mail@danielfett.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
