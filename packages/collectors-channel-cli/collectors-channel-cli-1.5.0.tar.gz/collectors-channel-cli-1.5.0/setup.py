# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['collectors_channel_cli']

package_data = \
{'': ['*']}

install_requires = \
['dnspython>=2.1.0,<3.0.0',
 'pymongo>=3.11.3,<4.0.0',
 'python-dotenv>=0.15.0,<0.16.0',
 'typer[all]>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['colcha = collectors_channel_cli.main:setup']}

setup_kwargs = {
    'name': 'collectors-channel-cli',
    'version': '1.5.0',
    'description': '',
    'long_description': '# collectors-channel-cli\nBuilt with ❤️ using [Typer](https://typer.tiangolo.com)\n\n\n## How to use it\n\nCreate a properties file at ``$HOME/.colcha/my.properties`` using this as an example: \n```\n# MongoDB\nMONGO_URL=mongodb+srv://user:password@url/database\n```\nOr pass ``--props`` to the CLI with the file location.\n\nCheck out the project at GitLab: https://gitlab.com/collectors-channel.\n',
    'author': 'Paulo Salgado',
    'author_email': 'pjosalgado@gmail.com',
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
