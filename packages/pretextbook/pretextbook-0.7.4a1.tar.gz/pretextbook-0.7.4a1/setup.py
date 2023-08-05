# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pretext', 'pretext.static']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.27,<4.0.0',
 'click-logging>=1.0.1,<2.0.0',
 'click>=8.1.3,<9.0.0',
 'ghp-import>=2.1.0,<3.0.0',
 'lxml>=4.9.0,<5.0.0',
 'pdfCropMargins>=1.0.8,<2.0.0',
 'requests>=2.28.0,<3.0.0',
 'single-version>=1.5.1,<2.0.0',
 'watchdog>=2.1.9,<3.0.0']

entry_points = \
{'console_scripts': ['pretext = pretext.cli:main']}

setup_kwargs = {
    'name': 'pretextbook',
    'version': '0.7.4a1',
    'description': 'A package to author, build, and deploy PreTeXt projects.',
    'long_description': None,
    'author': 'PreTeXtBook.org',
    'author_email': 'steven.clontz+PreTeXt@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.5,<4.0.0',
}


setup(**setup_kwargs)
