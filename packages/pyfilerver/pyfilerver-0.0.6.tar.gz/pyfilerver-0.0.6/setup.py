# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyfilerver']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['pyfilerver = pyfilerver:main']}

setup_kwargs = {
    'name': 'pyfilerver',
    'version': '0.0.6',
    'description': 'Python Http File Server: Added file upload function to `http.server`',
    'long_description': '# pyfilerver\n<p>\n    <a href="https://pypi.org/project/pyfilerver/" target="_blank">\n        <img src="https://img.shields.io/pypi/v/pyfilerver" />\n    </a>\n    <a href="https://github.com/IanVzs/pyfilerver/blob/main/.github/workflows/ci.yml" target="_blank">\n        <img src="https://img.shields.io/github/workflow/status/ianvzs/pyfilerver/CI" />\n    </a>\n    <a href="https://app.codecov.io/gh/ianvzs/pyfilerver" target="_blank">\n        <img src="https://img.shields.io/codecov/c/github/ianvzs/pyfilerver" />\n    </a>\n    <img src="https://img.shields.io/github/license/ianvzs/pyfilerver" />\n    <a href="https://pepy.tech/project/pyfilerver" target="_blank">\n        <img src="https://pepy.tech/badge/pyfilerver" />\n    </a>\n</p>\n\npython http file server\n\n## Install & Run\n### Source\n```bash\ngit clone git@github.com:IanVzs/pyfilerver.git\ncd pyfilerver\npython pyfilerver/main.py \n```\n\n### Pip\nMake sure you have pip installed.\n\n```bash\npip install pyfilerver\n```\n#### Local\n```\ngit clone git@github.com:IanVzs/pyfilerver.git\ncd pyfilerver\npip install .\npyfilerver\n```\n\n## Use\nWhen the program is running, use the web browser to access `http://127.0.0.1:8000/`. You can see\n\n![demo png](https://github.com/IanVzs/pyfilerver/blob/main/demo.png)\n\n### Custom Port\n```\npyfilerver 9000\n```\nSo you will need access `http://127.0.0.1:9000/`, All just like `http.server`.\n',
    'author': 'ianvzs',
    'author_email': 'ianvzs@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/IanVzs/pyfilerver',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
