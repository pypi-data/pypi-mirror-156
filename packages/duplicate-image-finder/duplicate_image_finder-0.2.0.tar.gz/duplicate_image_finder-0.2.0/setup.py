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

entry_points = \
{'console_scripts': ['duplicate-image-finder = entry:main']}

setup_kwargs = {
    'name': 'duplicate-image-finder',
    'version': '0.2.0',
    'description': 'duplicate image finder helps you find duplicate or similar images as well as delete them.',
    'long_description': '# Duplicate Image Finder\n\nDuplicate image finder uses image hashing to find similar/duplicate images in your local storage. All you gotta do is\n\n1. install\n2. install dependencies (using `poetry`)\n3. run it (using `poetry` maybe?)\n\nFor example:\n\n```sh\n# show help\npython duplicate_finder.py --help\n# add directory images and calculate hashes using 4 threads\npython duplicate_finder.py --add <directory> --parallel 4\n# show the duplicate/similar images found in your browser\npython duplicate_finder.py --show\n```\n## Poetry\n\nInstalling dependencies\n\n```sh\npoetry install\n```\n\nRunning\n\n```sh\npoetry run python duplicate_image_finder/duplicate_finder.py --show\n```\n\nTesting\n\n```sh\npoetry run pytest\n```\netc.\n\nThis duplicate image finder source code is inspired/partially copied from https://github.com/philipbl/duplicate-images.git.\n\nSignificant changes from the referred version are:\n\n1. moved from `mongodb` to `sqlite`\n2. Is probably better in terms of finding similar images (or perhaps I misunderstood the previous code)\n\nConcepts/Technologies I learned/tried to learn while doing this:\n\n1. `poetry` for dependency\n2. `pytest` for unit test\n3. `pysqlite3` for database\n4. `concurrency` for performance\n5. `imagehash` for perpetual image hashing for finding similarity\n6. grouping CLI arguments in python (mutually exclusive, etc) using `argparser`\n',
    'author': 'Amit',
    'author_email': 'lordamit@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/LordAmit/duplicate_image_finder',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
