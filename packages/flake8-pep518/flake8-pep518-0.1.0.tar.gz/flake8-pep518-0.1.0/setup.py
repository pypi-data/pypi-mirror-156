# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flake8_pep518']

package_data = \
{'': ['*']}

install_requires = \
['flake8>=4.0.1,<5.0.0']

extras_require = \
{':python_version < "3.11"': ['tomli>=2.0.1,<3.0.0']}

entry_points = \
{'flake8.extension': ['PRO = flake8_pep518.main:PyprojectExtension']}

setup_kwargs = {
    'name': 'flake8-pep518',
    'version': '0.1.0',
    'description': 'Flake8 plugin that allows specifying config in pyproject.toml.',
    'long_description': "# flake8-pep518\n\nFlake8 plugin that allows specifying config in pyproject.toml.\n\nThere are a lot of projects that do essentially the same thing, but only this one doesn't make you change the command. Also, it's deadly simple:\n\n```bash\npip install flake8-pep518\n```\n\nAnd that's it!\n\n## Usage\n\nInstall the plugin with the command above and move your Flake8 config to `pyproject.toml`.\n\n```setup.cfg\n[flake8]\nignore = E231, E241\nper-file-ignores =\n    __init__.py:F401\nmax-line-length = 88\ncount = true\n```\n\nRename `[flake8]` section to `[tool.flake8]` and convert everything else to TOML format.\n\n```pyproject.toml\n[tool.flake8]\nignore = ['E231', 'E241']\nper-file-ignores = [\n    '__init__.py:F401',\n]\nmax-line-length = 88\ncount = true\n```\n\nRun Flake8 as usuall.\n\n```bash\nflake8\n```\n\n## Inspiration\n\nInspired by [Flake8], [Flake9], [FlakeHeaven] and [Flake8-pyproject].\n\n## License\n\n**flake8-pep518** is licensed under the MIT. Please see [License.md] for more information.\n\n[Flake8]: https://github.com/pycqa/flake8\n[Flake9]: https://gitlab.com/retnikt/flake9\n[FlakeHeaven]: https://github.com/flakeheaven/flakeheaven\n[Flake8-pyproject]: https://github.com/john-hen/Flake8-pyproject\n[License.md]: https://github.com/aleksul/flake8-pep518/blob/main/LICENSE\n",
    'author': 'aleksul',
    'author_email': 'me@aleksul.space',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
