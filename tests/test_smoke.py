import matplotlib
import matplotlib.style

import evaplot
from evaplot.core import update_matplotlib_fonts


def test_import() -> None:
    assert evaplot.__version__ != ""


def test_styles_registered() -> None:
    evaplot_styles = [s for s in matplotlib.style.available if "evaplot" in s]
    assert len(evaplot_styles) > 0, "No evaplot styles found in matplotlib.style.available"


def test_update_matplotlib_fonts_runs() -> None:
    update_matplotlib_fonts()


def test_public_api() -> None:
    for name in evaplot.__all__:
        assert hasattr(evaplot, name), f"Missing public symbol: {name}"
