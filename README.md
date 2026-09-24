# latex2svg

Desktop app that converts plain LaTeX math into SVG, PNG or JPG. Built with PySide6 and matplotlib's mathtext engine. No LaTeX installation required.

## Features

- Type plain LaTeX with no `$` signs needed
- Live SVG preview
- Export to SVG, PNG or JPG
- Adjustable font size and text color
- Computer Modern font, so output looks like real LaTeX
- `Ctrl+Enter` to convert

## Requirements

- Python 3.10+
- PySide6, matplotlib, Pillow

## Install

```bash
git clone https://github.com/YOUR_USERNAME/latex2svg.git
cd latex2svg
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Usage

1. Type an expression, for example `\binom{n}{k} = \frac{n!}{k!(n-k)!}`
2. Press `Ctrl+Enter` or click **Convert to SVG**
3. Click **Save SVG...**, **Save as PNG** or **Save as JPG**

## Project structure

| File | Purpose |
|------|---------|
| `converter.py` | LaTeX to SVG/PNG/JPG conversion logic, independent of the UI |
| `main.py` | PySide6 interface |

`converter.py` can be imported on its own:

```python
from converter import latex_to_svg_bytes

svg = latex_to_svg_bytes(r"\frac{a}{b}", fontsize=24, color="black")
open("formula.svg", "wb").write(svg)
```

## Limitations

This uses matplotlib's mathtext, which supports only a subset of LaTeX math. Full LaTeX features such as `align`, matrix environments and packages are not supported.

## License

MIT. See [LICENSE](LICENSE).
