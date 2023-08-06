# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['saki']

package_data = \
{'': ['*']}

install_requires = \
['npyscreen>=4.10.5,<5.0.0', 'typer[all]>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['saki = saki.main:app']}

setup_kwargs = {
    'name': 'saki',
    'version': '1.1.1',
    'description': 'A simple alternative to the cat command line tool',
    'long_description': '# Saki\n\n![](https://www.beardsleyzoo.org/uploads/1/2/4/2/124214186/245_orig.jpg)\n\n## Desciption\n\nSaki is an alternative of the cat and nano command line tools.\n\n\n## Install \n\n### Windows\n    1. Go to cmd or powershell and run "pip install windows-curses"\n    2. Run "pip install saki"\n\n### Mac/Linux\n    1. Run "pip install saki" or "pip3 install saki" if the former doesn\'t work\n\n## Links\n\nGithub - https://github.com/Luke-Pitstick/saki\n\nPyPi - https://pypi.org/project/saki/\n\n\n',
    'author': 'Luke Pitstick',
    'author_email': 'lukepitstick06@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
