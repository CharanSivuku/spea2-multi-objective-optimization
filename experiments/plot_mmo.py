"""Decision-space and objective-space plots for the CEC 2020 MMO problems."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402,F401  (3-D projection needs this import)


def _scatter(ax, points, dims, **kwargs):
    if dims == 2:
        ax.scatter(points[:, 0], points[:, 1], **kwargs)
    else:
        ax.scatter(points[:, 0], points[:, 1], points[:, 2], **kwargs)


def plot_mmo(name, obtained_ps, obtained_pf, reference_ps, reference_pf, output_path, title_suffix=""):
    """Two panels: Pareto set (decision space) and Pareto front (objective space)."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(13, 5.5))

    for index, (obtained, reference, label, axes_names) in enumerate((
        (obtained_ps, reference_ps, "Pareto set (decision space)", "x"),
        (obtained_pf, reference_pf, "Pareto front (objective space)", "f"),
    )):
        dims = reference.shape[1]

        if dims not in (2, 3):
            raise ValueError("Plotting supports 2 or 3 dimensions")

        ax = fig.add_subplot(
            1, 2, index + 1, projection="3d" if dims == 3 else None
        )

        _scatter(ax, reference, dims, s=6, c="tab:red", alpha=0.35, label="Reference")
        _scatter(ax, obtained, dims, s=16, c="tab:blue", label="SPEA2")

        ax.set_xlabel(f"{axes_names}1")
        ax.set_ylabel(f"{axes_names}2")

        if dims == 3:
            ax.set_zlabel(f"{axes_names}3")

        ax.set_title(label)
        ax.legend(loc="best")

    fig.suptitle(f"{name} - SPEA2 {title_suffix}".strip())
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
