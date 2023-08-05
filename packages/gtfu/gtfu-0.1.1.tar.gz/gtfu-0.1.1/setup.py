# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gtfu']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.10.0,<5.0.0',
 'lxml>=4.8.0,<5.0.0',
 'pyperclip>=1.8.2,<2.0.0',
 'readchar>=3.0.5,<4.0.0',
 'requests>=2.27.1,<3.0.0',
 'rich>=12.0.1,<13.0.0']

entry_points = \
{'console_scripts': ['gtfu = gtfu.__main__:main']}

setup_kwargs = {
    'name': 'gtfu',
    'version': '0.1.1',
    'description': 'Command line tool to Get pageTitle From Url.',
    'long_description': '# gtfu\n\nCommand line tool to Get pageTitle From Url.\n\n## Installation\n\nIt supports Python 3.9+.\n\n```sh\npip install gtfu\n```\n\n## Usage\n\nAfter installation, type the following command into your terminal application.\n\n- ```sh\n  gtfu https://example.com/\n  ```\n\n  The page title will be copied to the clipboard.\n  - `Example Domain`\n\n- ```sh\n  gtfu -m https://example.com/\n  ```\n\n  The page title will be copied to the clipboard in markdown format.\n  - `[Example Domain](https://example.com/)`\n\n- ```sh\n  gtfu\n  ```\n\n  An interactive prompt will begin.\n',
    'author': 'seijinrosen',
    'author_email': '86702775+seijinrosen@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/seijinrosen',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
