"""Generate README.md by rendering a Jinja2 template with example plots."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402
import typer  # noqa: E402
from jinja2 import Environment, FileSystemLoader  # noqa: E402

import evaplot  # noqa: E402

app = typer.Typer()

_STYLES = [
    {"name": "evaplot_rc", "font": "Roboto Condensed"},
    {"name": "evaplot_fsc", "font": "Fira Sans Condensed"},
    {"name": "evaplot_j", "font": "Jost"},
    {"name": "evaplot_m", "font": "Montserrat"},
    {"name": "evaplot_sg", "font": "Space Grotesk"},
    {"name": "evaplot_tw", "font": "Titillium Web"},
]

_DEMO_DATA = pd.DataFrame(
    {
        "Category": ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"],
        "Value": [72, 85, 61, 90, 78],
    }
)


def _generate_style_plots(output_dir: Path) -> list[dict[str, str]]:
    results = []
    for entry in _STYLES:
        style_name = entry["name"]
        font_name = entry["font"]
        evaplot.set_style(style_name)
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(data=_DEMO_DATA, x="Category", y="Value", ax=ax)
        ax.set_title(f"{style_name}  ({font_name})")
        ax.set_xlabel("Category")
        ax.set_ylabel("Value")
        out = output_dir / f"style_{style_name}.png"
        fig.savefig(out, bbox_inches="tight", dpi=150)
        plt.close("all")
        results.append({**entry, "image": str(out)})
        typer.echo(f"  saved {out}")
    return results


def _generate_helper_plots(output_dir: Path) -> dict[str, str]:
    evaplot.set_style("evaplot_rc")
    helpers: dict[str, str] = {}

    # rotate_xticklabels
    long_cats = [
        "Very Long Label A",
        "Very Long Label B",
        "Very Long Label C",
        "Very Long Label D",
        "Very Long Label E",
        "Very Long Label F",
        "Very Long Label G",
        "Very Long Label H",
    ]
    values = [23, 45, 12, 67, 34, 89, 56, 44]
    rotate_data = pd.DataFrame({"Category": long_cats, "Value": values})
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    sns.barplot(data=rotate_data, x="Category", y="Value", ax=ax1)
    ax1.set_title("Default (overlapping labels)")
    sns.barplot(data=rotate_data, x="Category", y="Value", ax=ax2)
    ax2.set_title("After rotate_xticklabels(ax, 45)")
    evaplot.rotate_xticklabels(ax2, rotation=45)
    fig.tight_layout()
    out = output_dir / "helper_rotate_xticklabels.png"
    fig.savefig(out, bbox_inches="tight", dpi=150)
    plt.close("all")
    helpers["rotate_xticklabels"] = str(out)
    typer.echo(f"  saved {out}")

    # move_legend
    rng_data = pd.DataFrame(
        {
            "x": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "y": [2, 4, 3, 5, 6, 4, 7, 5, 8, 6, 5, 3, 7, 4, 8, 3, 6, 4, 7, 5],
            "group": ["A"] * 10 + ["B"] * 10,
        }
    )
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    sns.scatterplot(data=rng_data, x="x", y="y", hue="group", ax=ax1)
    ax1.set_title("Default legend position")
    sns.scatterplot(data=rng_data, x="x", y="y", hue="group", ax=ax2)
    ax2.set_title("After move_legend(...)")
    evaplot.move_legend(ax2, bbox_to_anchor=(0.5, -0.15), loc="upper center", ncol=2)
    fig.tight_layout()
    out = output_dir / "helper_move_legend.png"
    fig.savefig(out, bbox_inches="tight", dpi=150)
    plt.close("all")
    helpers["move_legend"] = str(out)
    typer.echo(f"  saved {out}")

    # adjust_layout
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    categories = ["A", "B", "C", "D"]
    for idx, ax in enumerate(axes.flat):
        vals = [10 + idx * 5, 20 + idx * 3, 15 + idx * 4, 25 + idx * 2]
        bar_data = pd.DataFrame({"Category": categories, "Value": vals})
        sns.barplot(data=bar_data, x="Category", y="Value", ax=ax)
        ax.set_title(f"Subplot {idx + 1}")
    evaplot.adjust_layout(fig=fig, hspace=0.35, wspace=0.3)
    out = output_dir / "helper_adjust_layout.png"
    fig.savefig(out, bbox_inches="tight", dpi=150)
    plt.close("all")
    helpers["adjust_layout"] = str(out)
    typer.echo(f"  saved {out}")

    # set_facet_col_titles — before
    facet_data = pd.DataFrame(
        {
            "group": ["Alpha"] * 5 + ["Beta"] * 5 + ["Gamma"] * 5,
            "x": list(range(5)) * 3,
            "y": [2, 4, 3, 5, 6, 3, 5, 4, 6, 7, 4, 6, 5, 7, 8],
        }
    )
    g = sns.FacetGrid(facet_data, col="group", height=4, aspect=1.0)
    g.map(sns.scatterplot, "x", "y")
    out_before = output_dir / "helper_set_facet_col_titles_before.png"
    g.fig.savefig(out_before, bbox_inches="tight", dpi=150)
    plt.close("all")
    helpers["set_facet_col_titles_before"] = str(out_before)
    typer.echo(f"  saved {out_before}")

    # set_facet_col_titles — after
    g = sns.FacetGrid(facet_data, col="group", height=4, aspect=1.0)
    g.map(sns.scatterplot, "x", "y")
    evaplot.set_facet_col_titles(g, "{col_name}")
    out_after = output_dir / "helper_set_facet_col_titles_after.png"
    g.fig.savefig(out_after, bbox_inches="tight", dpi=150)
    plt.close("all")
    helpers["set_facet_col_titles_after"] = str(out_after)
    typer.echo(f"  saved {out_after}")

    return helpers


@app.command()
def main(
    output_dir: Path = typer.Option(
        Path("docs/images"),
        "--output-dir",
        "-o",
        help="Directory where generated plot images are saved.",
    ),
    template: Path = typer.Option(
        Path("scripts/README.md.jinja2"),
        "--template",
        "-t",
        help="Path to the Jinja2 README template.",
    ),
    readme: Path = typer.Option(
        Path("README.md"),
        "--readme",
        "-r",
        help="Output path for the rendered README.",
    ),
) -> None:
    """Generate README.md by rendering a Jinja2 template with example plots."""
    if not Path("pyproject.toml").exists():
        typer.echo(
            "Error: pyproject.toml not found. Run this script from the repo root.",
            err=True,
        )
        raise typer.Exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    typer.echo("Generating style gallery plots...")
    style_entries = _generate_style_plots(output_dir)

    typer.echo("Generating helper function demo plots...")
    helper_entries = _generate_helper_plots(output_dir)

    # Make image paths relative to repo root for GitHub markdown links
    def _rel(path_str: str) -> str:
        p = Path(path_str)
        return str(p.relative_to(Path.cwd())) if p.is_absolute() else path_str

    for entry in style_entries:
        entry["image"] = _rel(entry["image"])
    helper_entries = {k: _rel(v) for k, v in helper_entries.items()}

    typer.echo("Rendering template...")
    env = Environment(
        loader=FileSystemLoader(str(template.parent)),
        keep_trailing_newline=True,
    )
    tmpl = env.get_template(template.name)
    rendered = tmpl.render(styles=style_entries, helpers=helper_entries)
    readme.write_text(rendered, encoding="utf-8")
    typer.echo(f"README written to {readme}")
