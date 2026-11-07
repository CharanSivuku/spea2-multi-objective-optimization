"""Plot objective-space approximations in 2D or 3D."""
from pathlib import Path
import matplotlib.pyplot as plt


def plot_front(approximation, reference, title: str, output_path: str) -> None:
    if not approximation:
        raise ValueError("Cannot plot an empty approximation")
    n_obj = len(approximation[0])
    if n_obj not in (2, 3):
        raise ValueError("Plotting currently supports 2 or 3 objectives")
    if any(len(p) != n_obj for p in approximation + reference):
        raise ValueError("Objective dimensions do not match")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(8, 6))
    if n_obj == 2:
        ax = fig.add_subplot(111)
        if reference:
            ax.scatter([p[0] for p in reference], [p[1] for p in reference], s=8, label="Reference front", alpha=.55)
        ax.scatter([p[0] for p in approximation], [p[1] for p in approximation], s=14, label="SPEA2 approximation")
        ax.set_xlabel("f1")
        ax.set_ylabel("f2")
    else:
        ax = fig.add_subplot(111, projection="3d")
        if reference:
            ax.scatter([p[0] for p in reference], [p[1] for p in reference], [p[2] for p in reference], s=5, label="Reference front", alpha=.35)
        ax.scatter([p[0] for p in approximation], [p[1] for p in approximation], [p[2] for p in approximation], s=12, label="SPEA2 approximation")
        ax.set_xlabel("f1")
        ax.set_ylabel("f2")
        ax.set_zlabel("f3")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
