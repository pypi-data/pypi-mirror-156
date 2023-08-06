import os
import warnings
from os.path import dirname, join

# get path to conffig files
from shutil import copy
from typing import Any, List

import matplotlib as mpl
import matplotlib.pyplot as plt
from cycler import Cycler
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
from matplotlib.style.core import reload_library
from seaborn.palettes import MPL_QUAL_PALS

import statworx_theme


def register_listed_cmap(colors: List[str], name: str) -> ListedColormap:
    """Register a listed colormat in matplotlib.

    Args:
        colors: Color of the colormap
        name: Name of the colormap

    Returns:
        Registered Colormap
    """
    # register color map
    cmap = ListedColormap(colors, N=len(colors), name=name)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        plt.register_cmap(name, cmap)

    # dark magic shit
    MPL_QUAL_PALS.update({name: len(colors)})
    return cmap


def register_blended_cmap(colors: List[str], name: str) -> LinearSegmentedColormap:
    """Register a blended colormap to matplotlib.

    Args:
        colors: Colors of the colormap
        name: Name of the colormap

    Returns:
        Registered Colormap
    """
    cmap = LinearSegmentedColormap.from_list(name, colors)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        plt.register_cmap(name, cmap)
    return cmap


def _install_styles() -> None:
    """Install matplotlib style files with suffix `.mplstyle` to the matplotlib config dir."""
    # list all theme files
    config_path = join(dirname(statworx_theme.__file__), "styles")
    theme_files = [join(config_path, f) for f in os.listdir(config_path)]

    # get config directory
    config_dir = mpl.get_configdir()
    style_dir = join(config_dir, "stylelib")
    os.makedirs(style_dir, exist_ok=True)

    # copy theme files into config directory
    for file in theme_files:
        copy(file, style_dir)

    # reload matplotlib
    reload_library()


def apply_style() -> None:
    """Apply the statworx color style."""
    _install_styles()
    plt.style.use("statworx")


def apply_custom_colors(
    colors: List[str], cmap_name: str = "stwx:custom", **kwargs: Any
) -> None:
    """Apply custom custom colors to statworx style.

    Args:
        colors: List of custom colors as hex codes
        cmap_name: Custom name of new colormap. Defaults to "stwx:custom".
        **kwargs: Addition parameters that are passed to the style config
    """
    # apply statworx style
    apply_style()

    # add colors as a custom cmap
    register_listed_cmap(colors, cmap_name)

    # add colors to current style
    color_list = [{"color": c} for c in colors]
    mpl.rcParams["axes.prop_cycle"] = Cycler(color_list)

    # apply kwargs
    mpl.rcParams.update(kwargs)
