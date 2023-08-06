# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['boggle']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0', 'tabulate>=0.8.10,<0.9.0']

entry_points = \
{'console_scripts': ['boggle = boggle.board:board_cli']}

setup_kwargs = {
    'name': 'boggle',
    'version': '0.1.1',
    'description': 'Generate boards for the game boggle',
    'long_description': "# Boggle\n\nThis project generates boards for the game boggle.\n\n## Installation\n\nThis package can be installed using pip.\n\n`pip install boggle`\n\n## Usage\n\n### CLI\n\nThis package exposes the `boggle` command in a shell.\n\n```bash\n$ boggle --help\nUsage: boggle [OPTIONS]\n\nOptions:\n  -s, --seed TEXT  A key to create a board from\n  --help           Show this message and exit.\n```\n\nIf a seed valaue is not provided, a random board will be returned:\n\n```bash\n$ boggle\n╒═══╤═══╤═══╤═══╕\n│ R │ S │ P │ L │\n├───┼───┼───┼───┤\n│ N │ H │ I │ L │\n├───┼───┼───┼───┤\n│ N │ T │ A │ W │\n├───┼───┼───┼───┤\n│ B │ U │ U │ T │\n╘═══╧═══╧═══╧═══╛\n$ boggle\n╒═══╤═══╤═══╤═══╕\n│ R │ F │ M │ B │\n├───┼───┼───┼───┤\n│ A │ N │ N │ R │\n├───┼───┼───┼───┤\n│ T │ E │ R │ S │\n├───┼───┼───┼───┤\n│ S │ D │ T │ T │\n╘═══╧═══╧═══╧═══╛\n```\n\nIf a seed value is provided, a board will be generated deterministically from the seed value:\n\n```bash\n$ boggle -s 'fish'\n╒═══╤═══╤═══╤═══╕\n│ T │ F │ R │ O │\n├───┼───┼───┼───┤\n│ E │ C │ E │ W │\n├───┼───┼───┼───┤\n│ H │ E │ J │ Y │\n├───┼───┼───┼───┤\n│ T │ N │ V │ W │\n╘═══╧═══╧═══╧═══╛\n$ boggle -s 'fish'\n╒═══╤═══╤═══╤═══╕\n│ T │ F │ R │ O │\n├───┼───┼───┼───┤\n│ E │ C │ E │ W │\n├───┼───┼───┼───┤\n│ H │ E │ J │ Y │\n├───┼───┼───┼───┤\n│ T │ N │ V │ W │\n╘═══╧═══╧═══╧═══╛\n$ boggle -s 'hamster'\n╒═══╤═══╤═══╤═══╕\n│ E │ O │ B │ T │\n├───┼───┼───┼───┤\n│ V │ T │ E │ H │\n├───┼───┼───┼───┤\n│ G │ E │ E │ H │\n├───┼───┼───┼───┤\n│ W │ U │ P │ F │\n╘═══╧═══╧═══╧═══╛\n$ boggle -s 'hamster'\n╒═══╤═══╤═══╤═══╕\n│ E │ O │ B │ T │\n├───┼───┼───┼───┤\n│ V │ T │ E │ H │\n├───┼───┼───┼───┤\n│ G │ E │ E │ H │\n├───┼───┼───┼───┤\n│ W │ U │ P │ F │\n╘═══╧═══╧═══╧═══╛\n```\n\n### Python Package\n\nImport the `boggle()` method from the `boggle` package:\n\n`from boggle import boggle`\n\nThis method will return a list of 16 boggle characters (including *Qu*). These are intended to be arranged into a\nsquare of four characters by four characters.\n\nIf a seed value is not provided, a random board will be returned:\n\n```python\n>>> from boggle import boggle\n>>> boggle()\n['B', 'A', 'S', 'T', 'H', 'U', 'M', 'H', 'R', 'P', 'E', 'R', 'O', 'T', 'O', 'N']\n>>> boggle()\n['A', 'E', 'T', 'L', 'E', 'E', 'W', 'D', 'E', 'D', 'J', 'T', 'Y', 'I', 'O', 'F']\n>>> boggle()\n['E', 'S', 'Y', 'F', 'V', 'X', 'N', 'Y', 'H', 'O', 'E', 'U', 'T', 'T', 'N', 'O']\n```\n\nIf a seed value is provided, a board will be generated deterministically from the seed value:\n\n```python\n>>> from boggle import boggle\n>>> boggle('fish')\n['T', 'F', 'R', 'O', 'E', 'C', 'E', 'W', 'H', 'E', 'J', 'Y', 'T', 'N', 'V', 'W']\n>>> boggle('fish')\n['T', 'F', 'R', 'O', 'E', 'C', 'E', 'W', 'H', 'E', 'J', 'Y', 'T', 'N', 'V', 'W']\n>>> boggle('hamster')\n['E', 'O', 'B', 'T', 'V', 'T', 'E', 'H', 'G', 'E', 'E', 'H', 'W', 'U', 'P', 'F']\n>>> boggle('hamster')\n['E', 'O', 'B', 'T', 'V', 'T', 'E', 'H', 'G', 'E', 'E', 'H', 'W', 'U', 'P', 'F']\n```\n\n&copy; Max Levine 2022\n",
    'author': 'Max Levine',
    'author_email': 'max@maxlevine.co.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/bmaximuml/boggle',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
