# --- File: converter.py (updated) ---
"""
converter.py
Core LaTeX -> SVG and PNG/JPG conversion logic using matplotlib's mathtext engine.
Kept separate from UI so it can be reused/tested independently.
"""

import io
import matplotlib
matplotlib.use("svg")  # headless backend, no GUI event loop conflict with Qt
import matplotlib.pyplot as plt


class LatexToSvgError(Exception):
    """Raised when matplotlib fails to parse/render the given LaTeX."""
    pass


def latex_to_svg_bytes(latex_expr: str, fontsize: int = 24,
                       color: str = "black", dpi: int = 300) -> bytes:
    """
    Convert a plain LaTeX math expression into SVG bytes.

    latex_expr: raw LaTeX WITHOUT surrounding $ signs, e.g. r"\\frac{n!}{k!(n-k)!}"
    Returns: SVG file content as bytes (ready to write to disk or feed to QSvgWidget).
    """
    matplotlib.rcParams["mathtext.fontset"] = "cm"  # Computer Modern -> looks like real LaTeX
    matplotlib.rcParams["svg.fonttype"] = "path"    # embed glyphs as paths, not font refs

    fig = plt.figure(figsize=(0.01, 0.01))
    try:
        fig.text(0, 0, f"${latex_expr}$", fontsize=fontsize, color=color)
    except Exception as e:
        plt.close(fig)
        raise LatexToSvgError(f"Failed to parse LaTeX: {e}") from e

    buf = io.BytesIO()
    try:
        fig.savefig(buf, format="svg", bbox_inches="tight",
                    transparent=True, pad_inches=0.08, dpi=dpi)
    except Exception as e:
        plt.close(fig)
        raise LatexToSvgError(f"Failed to render SVG: {e}") from e

    plt.close(fig)
    buf.seek(0)
    return buf.read()


def latex_to_png_bytes(latex_expr: str, fontsize: int = 24,
                       color: str = "black", dpi: int = 300) -> bytes:
    """
    Convert a plain LaTeX math expression into PNG bytes.

    Returns: PNG file content as bytes (ready to write to disk or feed to QLabel/QImage).
    """
    matplotlib.rcParams["mathtext.fontset"] = "cm"
    matplotlib.rcParams["svg.fonttype"] = "path"  # ensures clean rendering

    fig = plt.figure(figsize=(0.01, 0.01))
    try:
        fig.text(0, 0, f"${latex_expr}$", fontsize=fontsize, color=color)
    except Exception as e:
        plt.close(fig)
        raise LatexToSvgError(f"Failed to parse LaTeX: {e}") from e

    buf = io.BytesIO()
    try:
        fig.savefig(buf, format="png", bbox_inches="tight",
                    transparent=False, pad_inches=0.08, dpi=dpi)
    except Exception as e:
        plt.close(fig)
        raise LatexToSvgError(f"Failed to render PNG: {e}") from e

    plt.close(fig)
    buf.seek(0)
    return buf.read()


def latex_to_jpg_bytes(latex_expr: str, fontsize: int = 24,
                       color: str = "black", dpi: int = 300) -> bytes:
    """
    Convert a plain LaTeX math expression into JPG bytes.

    Returns: JPG file content as bytes (ready to write to disk).
    """
    matplotlib.rcParams["mathtext.fontset"] = "cm"
    matplotlib.rcParams["svg.fonttype"] = "path"

    fig = plt.figure(figsize=(0.01, 0.01))
    try:
        fig.text(0, 0, f"${latex_expr}$", fontsize=fontsize, color=color)
    except Exception as e:
        plt.close(fig)
        raise LatexToSvgError(f"Failed to parse LaTeX: {e}") from e

    buf = io.BytesIO()
    try:
        fig.savefig(buf, format="jpg", bbox_inches="tight",
                    transparent=False, pad_inches=0.08, dpi=dpi)
    except Exception as e:
        plt.close(fig)
        raise LatexToSvgError(f"Failed to render JPG: {e}") from e

    plt.close(fig)
    buf.seek(0)
    return buf.read()
