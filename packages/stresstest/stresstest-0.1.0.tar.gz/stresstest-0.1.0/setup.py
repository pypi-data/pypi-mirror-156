# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['stresstest',
 'stresstest.stresstests',
 'stresstest.stresstests.compute',
 'stresstest.stresstests.interpreter',
 'stresstest.stresstests.io',
 'stresstest.stresstests.os']

package_data = \
{'': ['*']}

install_requires = \
['rich']

entry_points = \
{'console_scripts': ['stresstest = stresstest.__main__:main']}

setup_kwargs = {
    'name': 'stresstest',
    'version': '0.1.0',
    'description': 'Stress test your system and Python interpreter.',
    'long_description': None,
    'author': 'Tomas Krejci',
    'author_email': 'tomas@krej.ci',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0.0',
}


setup(**setup_kwargs)
