import logging
import re
import time
from pathlib import Path
from tempfile import NamedTemporaryFile

import colormaps as cmaps
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager as fm

import requests
from fontTools import ttLib

log = logging.getLogger(__name__)

_FONT_CACHE_DIR = Path(mpl.get_cachedir()) / "opinionated_fonts"


###############################################################################
# Font management


def download_googlefont(font: str = "Roboto Condensed", add_to_cache: bool = False) -> None:
    """Download a font from Google Fonts and persist it to the matplotlib cache.

    Code adapted from Leland McInnes' datamapplot library.
    """
    _FONT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    api_fontname = font.replace(" ", "+")
    api_response = requests.get(
        f"https://fonts.googleapis.com/css?family={api_fontname}:black,bold,regular,light"
    )
    api_response.raise_for_status()
    font_urls = re.findall(r"(https?://[^\)]+)", str(api_response.content))
    for font_url in font_urls:
        font_data = requests.get(font_url)
        font_data.raise_for_status()
        with NamedTemporaryFile(delete=False, suffix=".ttf") as f:
            f.write(font_data.content)
            tmp_path = Path(f.name)
        tt = ttLib.TTFont(tmp_path)
        family_name = tt["name"].getDebugName(1)
        dest = _FONT_CACHE_DIR / tmp_path.name
        tmp_path.rename(dest)
        fm.fontManager.addfont(str(dest))
        log.debug("Added new font as %s", family_name)

    if add_to_cache:
        update_matplotlib_fonts()


def _is_font_cached(font: str) -> bool:
    if not _FONT_CACHE_DIR.exists():
        return False
    normalized = font.replace(" ", "").lower()
    return any(normalized in f.name.lower() for f in _FONT_CACHE_DIR.iterdir())


def download_font_with_retry(font: str, retries: int = 3, delay: int = 3) -> None:
    """Download a Google Font with retry logic."""
    for attempt in range(retries):
        try:
            log.debug("Downloading font: %s", font)
            download_googlefont(font=font)
            return
        except Exception as e:
            if attempt < retries - 1:
                log.debug(
                    "Attempt %d to download %s failed: %s. Retrying in %ds.",
                    attempt + 1, font, e, delay,
                )
                time.sleep(delay)
            else:
                log.debug("All attempts to download %s failed.", font)
                raise


def update_matplotlib_fonts() -> None:
    """Register all fonts from the download cache with matplotlib."""
    if not _FONT_CACHE_DIR.exists():
        return
    for font_file in fm.findSystemFonts(fontpaths=str(_FONT_CACHE_DIR)):
        if font_file.endswith((".ttf", ".otf")):
            try:
                fm.fontManager.addfont(font_file)
            except Exception as e:
                log.debug("Could not add font %s: %s", font_file, e)


###############################################################################
# Style


def set_cat_palette(n: int = 8) -> list[str]:
    """Set the categorical color palette based on the number of categories needed.

    Uses cmaps.dark2 for n <= 8, cmaps.vivid for larger sets.
    Returns the palette as a list of hex color strings for reuse in matplotlib.
    """
    palette = cmaps.vivid if n > 8 else cmaps.dark2
    hex_colors = [mpl.colors.to_hex(c) for c in palette.colors]
    sns.set_palette(hex_colors)
    return hex_colors


def set_style(style: str = "opinionated_rc", n: int = 8) -> None:
    """Apply the opinionated matplotlib style and categorical palette.

    Equivalent to:
        plt.style.use(style)
        opinionated_v2.set_cat_palette(n)
    """
    plt.style.use(style)
    set_cat_palette(n)


###############################################################################
# Plot helpers


def rotate_xticklabels(ax: mpl.axes.Axes, rotation: int = 45, ha: str = "right") -> None:
    """Rotate x-axis tick labels on the given axes."""
    plt.setp(ax.get_xticklabels(), rotation=rotation, ha=ha)


def move_legend(
    obj: object,
    bbox_to_anchor: tuple[float, float] = (0.4, -0.0001),
    loc: str = "upper center",
    ncol: int = 3,
    fontsize: int = 12,
    title_fontsize: int = 14,
    **kwargs: object,
) -> None:
    """Move a seaborn legend with sensible defaults for bottom-centered placement."""
    sns.move_legend(
        obj,
        bbox_to_anchor=bbox_to_anchor,
        loc=loc,
        ncol=ncol,
        fontsize=fontsize,
        title_fontsize=title_fontsize,
        **kwargs,
    )


def adjust_layout(
    fig: mpl.figure.Figure | None = None,
    hspace: float = 0.2,
    wspace: float = 0.2,
    bottom: float = 0.1,
    rect: tuple[float, float, float, float] = (0.03, 0.06, 0.97, 0.95),
) -> None:
    """Adjust subplot spacing and apply tight_layout.

    Pass a figure explicitly (e.g. ``g.fig`` for a seaborn FacetGrid) or leave
    as None to operate on the current figure.
    """
    if fig is None:
        fig = plt.gcf()
    fig.subplots_adjust(hspace=hspace, wspace=wspace, bottom=bottom)
    fig.tight_layout(rect=rect)


def set_facet_col_titles(g: object, template: str = "{col_name}") -> None:
    """Set FacetGrid column titles using a concise template (default: just the column value)."""
    g.set_titles(col_template=template)  # type: ignore[union-attr]
