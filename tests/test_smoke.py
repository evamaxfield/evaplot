import matplotlib
import matplotlib.style

import opinionated_v2
from opinionated_v2.core import update_matplotlib_fonts


def test_import() -> None:
    assert opinionated_v2.__version__ != ""


def test_styles_registered() -> None:
    opinionated_styles = [s for s in matplotlib.style.available if "opinionated" in s]
    assert len(opinionated_styles) > 0, "No opinionated styles found in matplotlib.style.available"


def test_update_matplotlib_fonts_runs() -> None:
    update_matplotlib_fonts()


def test_public_api() -> None:
    for name in opinionated_v2.__all__:
        assert hasattr(opinionated_v2, name), f"Missing public symbol: {name}"
