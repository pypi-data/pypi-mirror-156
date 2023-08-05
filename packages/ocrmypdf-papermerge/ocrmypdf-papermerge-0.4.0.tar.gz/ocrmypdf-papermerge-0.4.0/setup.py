# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ocrmypdf_papermerge']

package_data = \
{'': ['*'], 'ocrmypdf_papermerge': ['templates/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0', 'lxml>=4.9.0,<5.0.0', 'ocrmypdf>=13.5.0,<14.0.0']

setup_kwargs = {
    'name': 'ocrmypdf-papermerge',
    'version': '0.4.0',
    'description': 'OCRmyPDF plugin to generate SVG files for Papermerge',
    'long_description': None,
    'author': 'Eugen Ciur',
    'author_email': 'eugen@papermerge.com',
    'maintainer': 'Eugen Ciur',
    'maintainer_email': 'eugen@papermerge.com',
    'url': 'https://github.com/papermerge/OCRmyPDF_papermerge',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)
