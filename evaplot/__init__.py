"""Top-level package for evaplot."""

from importlib.metadata import PackageNotFoundError, version
from importlib.resources import files

import matplotlib as mpl

try:
    __version__ = version("evaplot")
except PackageNotFoundError:
    __version__ = "uninstalled"

__author__ = "Eva Maxfield Brown"
__email__ = "evamaxfieldbrown@gmail.com"

from .core import (
    _is_font_cached,
    adjust_layout,
    download_font_with_retry,
    download_googlefont,
    move_legend,
    rotate_xticklabels,
    set_cat_palette,
    set_facet_col_titles,
    set_style,
    show_installed_fonts,
    update_matplotlib_fonts,
)

__all__ = [
    "adjust_layout",
    "download_googlefont",
    "move_legend",
    "rotate_xticklabels",
    "set_cat_palette",
    "set_facet_col_titles",
    "set_style",
    "show_installed_fonts",
    "update_matplotlib_fonts",
]

# Register bundled stylesheets with matplotlib
_data_path = str(files("evaplot") / "data")
_opinionated_styles = mpl.style.core.read_style_directory(_data_path)
mpl.style.reload_library()  # reload first — clears library before we add custom styles
mpl.style.core.update_nested_dict(mpl.style.library, _opinionated_styles)
mpl.style.available[:] = sorted(mpl.style.library.keys())

# Register bundled fonts
update_matplotlib_fonts()

# Download any missing Google Fonts to the matplotlib cache on first use
_FONTS = [
    "Roboto Condensed",
    "Montserrat",
    "Source Code Pro",
    "Fira Sans",
    "Fira Sans Condensed",
    "IBM Plex Sans",
    "Space Grotesk",
    "Space Mono",
    "Roboto",
    "Jost",
    "Titillium Web",
]

for _font in _FONTS:
    if not _is_font_cached(_font):
        download_font_with_retry(_font)
