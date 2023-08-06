# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['internal_match_hooks']

package_data = \
{'': ['*'], 'internal_match_hooks': ['resources/variables/*']}

setup_kwargs = {
    'name': 'internal-match-hooks',
    'version': '0.1.0',
    'description': 'A replaCy match hoold lib',
    'long_description': '# internal-match-hooks\nshared lib for replacy match hooks ',
    'author': 'Sam Havens',
    'author_email': 'sam.havens@writer.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.writer.ai/nlp/internal-match-hooks',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
