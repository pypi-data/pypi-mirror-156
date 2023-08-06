# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['deltaman']

package_data = \
{'': ['*']}

extras_require = \
{'building': ['lark>=1.1.2,<2.0.0'],
 'testing': ['pytest>=7.1.2,<8.0.0', 'tox>=3.25.0,<4.0.0']}

setup_kwargs = {
    'name': 'deltaman',
    'version': '0.0.4',
    'description': 'Parsing human time intervals',
    'long_description': '# Deltaman - Parsing human time intervals\n\n```shell\npip install deltaman\n```\n\n## Getting Started\n\n```python\nfrom deltaman import delta_parser\n\nfor delta in ("15s", "3min", "1h15m", "1 day 12 hours", "1m-15s"):\n    parsed = delta_parser.parse(delta)\n    print(f\'{delta!r:20s} {parsed!r:20s}\')\n```\n\nThat outputs\n\n```\n\'15s\'                datetime.timedelta(seconds=15)\n\'3min\'               datetime.timedelta(seconds=180)\n\'1h15m\'              datetime.timedelta(seconds=4500)\n\'1 day 12 hours\'     datetime.timedelta(days=1, seconds=43200)\n\'1m-15s\'             datetime.timedelta(seconds=45)\n```\n\nNote you can get more examples from the testing files.\n\n## Testing\n\n```shell\n$ pytest\n```\n\nOr\n\n```shell\n$ tox\n```\n',
    'author': 'Wonder',
    'author_email': 'wonderbeyond@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/wonderbeyond/deltaman',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
