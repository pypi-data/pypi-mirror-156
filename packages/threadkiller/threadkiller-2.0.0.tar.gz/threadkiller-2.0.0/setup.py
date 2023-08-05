# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['threadkiller']

package_data = \
{'': ['*']}

install_requires = \
['cfig[cli]>=0.2.3,<0.3.0', 'python-telegram-bot>=20.0a1,<21.0']

entry_points = \
{'console_scripts': ['threadkiller = threadkiller.__main__:main']}

setup_kwargs = {
    'name': 'threadkiller',
    'version': '2.0.0',
    'description': 'A Telegram bot to delete messages sent outside of threads',
    'long_description': '# Threadkiller!\n\n_A Telegram bot to delete messages sent outside of channel comment threads_\n\n\\[ [**Bot**](https://t.me/threadkillerbot) | [Documentation](https://github.com/Steffo99/threadkiller/wiki) \\]\n\n',
    'author': 'Stefano Pigozzi',
    'author_email': 'me@steffo.eu',
    'maintainer': 'Stefano Pigozzi',
    'maintainer_email': 'me@steffo.eu',
    'url': 'https://github.com/Steffo99/threadkiller/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
