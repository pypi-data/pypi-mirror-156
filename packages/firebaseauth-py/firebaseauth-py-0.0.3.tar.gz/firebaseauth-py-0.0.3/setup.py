# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['firebaseauth_py']

package_data = \
{'': ['*']}

install_requires = \
['build>=0.8.0,<0.9.0', 'requests>=2.28.0,<3.0.0', 'twine>=4.0.1,<5.0.0']

setup_kwargs = {
    'name': 'firebaseauth-py',
    'version': '0.0.3',
    'description': "Unofficial API wrapper for Firebase Auth's REST API",
    'long_description': '# Firebase Auth API Wrapper\n\n> A simple api wrapper for Firebase Auth services ([Reference](https://firebase.google.com/docs/reference/rest/auth))\n',
    'author': 'Justin Chiou',
    'author_email': 'chiou.kai@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
