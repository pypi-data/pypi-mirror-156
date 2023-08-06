# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yagls']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp']

setup_kwargs = {
    'name': 'yagls',
    'version': '1.0.1',
    'description': 'Yet another Github Label Synchroniser',
    'long_description': "# yagls\nYet Another Github Label Synchroniser.\n## Inspiration\nI wanted to labeling well. But I'd no idea, so I found well-labeled project.\n\nAlso I found another Github Label Synchroniser, but It wasn't fit to me.\n\nTo me, that wasn't intuitive. That worked well, but I didn't like that.\n\nSo I decided to make new Github Label Synchroniser.\n## Feather\nJust copy labels from repository and paste to repository.",
    'author': 'preeded',
    'author_email': '86511859+preeded@users.noreply.github.com',
    'maintainer': 'preeded',
    'maintainer_email': '86511859+preeded@users.noreply.github.com',
    'url': 'https://github.com/preeded/ygl',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
