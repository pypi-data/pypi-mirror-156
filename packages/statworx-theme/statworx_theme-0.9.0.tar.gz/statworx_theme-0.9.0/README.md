# Statworx Theme

[![PyPI version](https://badge.fury.io/py/statworx-theme.svg)](https://badge.fury.io/py/statworx-theme)
[![Documentation Status](https://readthedocs.org/projects/statworx-theme/badge/?version=latest)](https://statworx-theme.readthedocs.io/en/latest/?badge=latest)
[![Release](https://github.com/STATWORX/statworx-theme/actions/workflows/release.yml/badge.svg)](https://github.com/STATWORX/statworx-theme/actions/workflows/release.yml)
[![Code Quality](https://github.com/STATWORX/statworx-theme/actions/workflows/conde_quality.yml/badge.svg)](https://github.com/STATWORX/statworx-theme/actions/workflows/conde_quality.yml)
[![Python version](https://img.shields.io/badge/python-3.8-blue.svg)](https://pypi.org/project/kedro/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/STATWORX/statworx-theme/blob/master/LICENSE)
![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)

A color theme plugin for the [matplotlib](https://matplotlib.org/) library and all its derivatives, which automatically applies the official statworx color theme.
This package also registers commonly used [qualitative color maps](https://matplotlib.org/stable/tutorials/colors/colormaps.html) (such as a fade from good to bad) for use in presentations.

![Sample](./docs/assets/sample.svg)

## Quick Start

Simply install a module with `pip` by using the following command.

```console
pip install statworx-theme
```

To apply the style, you must call the `apply_style` function by typing:

```python
from statworx_theme import apply_style
apply_style()
```

## Gallery

There is an extensive gallery of figures that use the Statworx theme that you can draw inspiration from. You can find it [here](https://statworx-theme.readthedocs.io/en/latest/gallery.html).

![Sample](./docs/assets/gallery.png)

## Custom Colors

You can also use a custom list of color for the color scheme beside the official statworx colors.
There is a convenience function for that which is described below.
This simply changes the colors.
In case you want to change the entire style you should implement your own `.mplstyle` file (see [this](https://matplotlib.org/stable/tutorials/introductory/customizing.html)).

```python
from statworx_theme import apply_custom_colors

custom_colors = [
    DARK_BLUE := "#0A526B",
    DARK_RED := "#6B0020",
    GREY := "#808285",
]
apply_custom_colors(custom_colors)
```
