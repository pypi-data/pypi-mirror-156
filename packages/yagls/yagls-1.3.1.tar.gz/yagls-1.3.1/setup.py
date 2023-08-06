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
    'version': '1.3.1',
    'description': 'Yet Another Github Label Synchroniser',
    'long_description': "# yagls\nYet Another Github Label Synchroniser.\n## Inspiration\nI wanted to be good at labeling at GitHub. Therefore, for reference, I searched for well-labeled repositories.\n\nHowever, it was hard work to carry the labels of the repository on a single way. I looked up Github Label Synchroniser to find some efficient way, but I didn't like they.\n\nThat's why I made the Yet Another Github Label Synchronizer.\n\n## Feather\n* Copy and paste labels from the repository\n* Save token\n* Automatically navigate through repositories with only the name of the repository\n",
    'author': 'preeded',
    'author_email': '86511859+preeded@users.noreply.github.com',
    'maintainer': 'preeded',
    'maintainer_email': '86511859+preeded@users.noreply.github.com',
    'url': 'https://github.com/github-labels/yagls',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
