# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['prettierjson']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['prettierjson = prettierjson.__main__:main']}

setup_kwargs = {
    'name': 'prettierjson',
    'version': '1.0.1',
    'description': 'Generate prettier and more compact JSON dumps',
    'long_description': '# prettierjson\n\n[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg?style=flat-square)](https://www.python.org/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)\n[![Github release](https://img.shields.io/badge/release-1.0.1-blue.svg?style=flat-square)](https://github.com/brianburwell11/prettierjson/releases/tag/1.0.1)\n[![PyPi](https://img.shields.io/badge/-PyPi-white.svg?logo=pypi&labelColor=4B8BBE&logoColor=FFD43B&style=flat-square)](https://pypi.org/project/prettierjson/)\n[![Documentation](https://img.shields.io/badge/-Documentation-2980b9.svg?logo=readthedocs&labelColor=2980b9&logoColor=FFFFFF&style=flat-square)][documentation]\n\nGenerate prettier and more compact JSON dumps\n\n## Installation\n\n**prettierjson** can be installed using one of these commands:\n\n```sh\npip install prettierjson\n```\n\n```sh\npoetry add prettierjson\n```\n\n## Usage\n\n### in python scripts\n\nprettierjson offers one function `prettierjson.dumps()` which is intended to be used as a drop-in replacement for `json.dumps()`\n\n```python\nfrom prettierjson import dumps\n\nmy_dictionary = {"foo": bar}\n\nwith open("foobar.json", "w") as f:\n    f.write(dumps(my_dictionary))\n```\n\nIf prettierjson needs to exist within the same module as the built-in json package _without overriding_ the default `json.dumps()`, the entire package should be imported in order to avoid namespace collisions\n```python\nimport json\nimport prettierjson\n\nmy_dictionary = {"foo": bar}\n\nwith open("builtin.json", "w") as f:\n    f.write(json.dumps(my_dictionary))\nwith open("prettierjson.json", "w") as f:\n    f.write(prettierjson.dumps(my_dictionary))\n```\n\nSee [the documentation][documentation] for more details.\n\n\n### as a command line interface\n\nprettierjson has a `__main__` module which allows it to be called directly when installed with the command `python -m prettierjson`.\n\nIn this way, prettierjson can be used to "prettify" one or multiple JSON files in-place by passing them as arguments\n```sh\n$ python -m prettierjson PATH/TO/JSON/FILE1.json PATH/TO/JSON/FILE2.json\n```\n\nIndent size and max line length can be set with the `--indent` and `--line-length` flags\n```sh\n$ python -m prettierjson --indent=2 --line-length=88 PATH/TO/JSON/FILE.json\n```\n\nRun `python -m prettierjson -h` for more command line usage details.\n\n\n<!-- links -->\n[poetry]: https://python-poetry.org/docs/\n[changelog]: docs/CHANGELOG.md\n[documentation]: https://github.com/brianburwell11/prettierjson/wiki\n',
    'author': 'Brian Burwell',
    'author_email': 'brianburwell11@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/brianburwell11/prettierjson',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
