# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['statworx_theme']

package_data = \
{'': ['*'], 'statworx_theme': ['styles/*']}

install_requires = \
['seaborn>=0.11.2,<0.12.0']

setup_kwargs = {
    'name': 'statworx-theme',
    'version': '0.9.0',
    'description': 'A color theme for matplotlib using the offical statworx design',
    'long_description': '# Statworx Theme\n\n[![PyPI version](https://badge.fury.io/py/statworx-theme.svg)](https://badge.fury.io/py/statworx-theme)\n[![Documentation Status](https://readthedocs.org/projects/statworx-theme/badge/?version=latest)](https://statworx-theme.readthedocs.io/en/latest/?badge=latest)\n[![Release](https://github.com/STATWORX/statworx-theme/actions/workflows/release.yml/badge.svg)](https://github.com/STATWORX/statworx-theme/actions/workflows/release.yml)\n[![Code Quality](https://github.com/STATWORX/statworx-theme/actions/workflows/conde_quality.yml/badge.svg)](https://github.com/STATWORX/statworx-theme/actions/workflows/conde_quality.yml)\n[![Python version](https://img.shields.io/badge/python-3.8-blue.svg)](https://pypi.org/project/kedro/)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/STATWORX/statworx-theme/blob/master/LICENSE)\n![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)\n\nA color theme plugin for the [matplotlib](https://matplotlib.org/) library and all its derivatives, which automatically applies the official statworx color theme.\nThis package also registers commonly used [qualitative color maps](https://matplotlib.org/stable/tutorials/colors/colormaps.html) (such as a fade from good to bad) for use in presentations.\n\n![Sample](./docs/assets/sample.svg)\n\n## Quick Start\n\nSimply install a module with `pip` by using the following command.\n\n```console\npip install statworx-theme\n```\n\nTo apply the style, you must call the `apply_style` function by typing:\n\n```python\nfrom statworx_theme import apply_style\napply_style()\n```\n\n## Gallery\n\nThere is an extensive gallery of figures that use the Statworx theme that you can draw inspiration from. You can find it [here](https://statworx-theme.readthedocs.io/en/latest/gallery.html).\n\n![Sample](./docs/assets/gallery.png)\n\n## Custom Colors\n\nYou can also use a custom list of color for the color scheme beside the official statworx colors.\nThere is a convenience function for that which is described below.\nThis simply changes the colors.\nIn case you want to change the entire style you should implement your own `.mplstyle` file (see [this](https://matplotlib.org/stable/tutorials/introductory/customizing.html)).\n\n```python\nfrom statworx_theme import apply_custom_colors\n\ncustom_colors = [\n    DARK_BLUE := "#0A526B",\n    DARK_RED := "#6B0020",\n    GREY := "#808285",\n]\napply_custom_colors(custom_colors)\n```\n',
    'author': 'statworx Team',
    'author_email': 'accounts@statworx.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://statworx-theme.readthedocs.io/en/latest',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
