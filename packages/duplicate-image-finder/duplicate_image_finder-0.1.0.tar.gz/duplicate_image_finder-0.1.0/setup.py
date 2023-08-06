# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['duplicate_image_finder']

package_data = \
{'': ['*']}

install_requires = \
['Flask-Cors>=3.0.10,<4.0.0',
 'Flask>=2.1.2,<3.0.0',
 'ImageHash>=4.2.1,<5.0.0',
 'Jinja2>=3.1.2,<4.0.0',
 'Pillow>=9.1.1,<10.0.0',
 'pandas>=1.4.2,<2.0.0',
 'python-magic-bin==0.4.14',
 'termcolor>=1.1.0,<2.0.0',
 'types-termcolor>=1.1.4,<2.0.0']

setup_kwargs = {
    'name': 'duplicate-image-finder',
    'version': '0.1.0',
    'description': 'duplicate image finder helps you find duplicate or similar images as well as delete them.',
    'long_description': None,
    'author': 'Amit',
    'author_email': 'lordamit@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
