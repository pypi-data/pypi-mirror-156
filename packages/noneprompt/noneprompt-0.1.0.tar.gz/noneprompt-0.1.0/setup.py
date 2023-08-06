# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['noneprompt', 'noneprompt.cli', 'noneprompt.prompts']

package_data = \
{'': ['*']}

install_requires = \
['prompt-toolkit>=3.0.19,<4.0.0']

entry_points = \
{'console_scripts': ['noneprompt = noneprompt.__main__:main']}

setup_kwargs = {
    'name': 'noneprompt',
    'version': '0.1.0',
    'description': 'Prompt toolkit for console interaction',
    'long_description': '# NonePrompt\n\nPrompt toolkit for console interaction\n',
    'author': 'yanyongyu',
    'author_email': 'yyy@nonebot.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nonebot/noneprompt',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
