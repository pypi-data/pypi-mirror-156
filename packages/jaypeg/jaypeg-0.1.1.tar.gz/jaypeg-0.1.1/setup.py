# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jaypeg']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.1.1,<10.0.0', 'filetype>=1.0.13,<2.0.0', 'typer[all]>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['jaypeg = jaypeg.main:app']}

setup_kwargs = {
    'name': 'jaypeg',
    'version': '0.1.1',
    'description': 'A command line tool for converting and resizing image files',
    'long_description': '# Jaypeg\n\nA command line tool for converting and re-sizing image files.\n\n## installation\n\n## usage\n\n## licence\n',
    'author': 'apjanco',
    'author_email': 'apjanco@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
