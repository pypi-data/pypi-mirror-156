# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gnomadapi']

package_data = \
{'': ['*']}

install_requires = \
['chromedriver-binary-auto==0.1.2',
 'chromedriver-binary>=104.0.5112,<105.0.0',
 'glob2>=0.7,<0.8',
 'selenium==4.2.0']

entry_points = \
{'console_scripts': ['gnomadAPI = gnomadapi.__main__:main']}

setup_kwargs = {
    'name': 'gnomadapi',
    'version': '1.0.0',
    'description': 'selenium wrapper to access gnomad db from the cmd',
    'long_description': None,
    'author': 'StephanHolgerD',
    'author_email': 'stephdruk@googlemail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
