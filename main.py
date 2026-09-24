"""
main.py
PySide6 desktop app: type plain LaTeX, preview the compiled SVG, save to disk.
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPlainTextEdit, QPushButton, QLabel, QFileDialog, QMessageBox,
    QSpinBox, QColorDialog, QSplitter
)
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from converter import latex_to_svg_bytes, latex_to_jpg_bytes, latex_to_png_bytes, LatexToSvgError

class LatexToSvgWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LaTeX → SVG / PNG / JPG Converter")
        self.resize(900, 500)

        self._current_svg_bytes: bytes | None = None
        self._text_color = QColor("black")

        self._build_ui()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)

        splitter = QSplitter(Qt.Horizontal)
        root_layout.addWidget(splitter, stretch=1)

        # ---- Left panel: input ----
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        left_layout.addWidget(QLabel("Enter plain LaTeX (no $ signs needed):"))

        self.latex_input = QPlainTextEdit()
        self.latex_input.setPlaceholderText(
            r"e.g.  \binom{n}{k} = \frac{n!}{k!(n-k)!}"
        )
        self.latex_input.setPlainText(r"\binom{n}{k} = \frac{n!}{k!(n-k)!}")
        left_layout.addWidget(self.latex_input, stretch=1)

        # font size + color controls
        controls_row = QHBoxLayout()

        controls_row.addWidget(QLabel("Font size:"))
        self.fontsize_spin = QSpinBox()
        self.fontsize_spin.setRange(8, 96)
        self.fontsize_spin.setValue(24)
        controls_row.addWidget(self.fontsize_spin)

        self.color_btn = QPushButton("Text Color")
        self.color_btn.clicked.connect(self._pick_color)
        controls_row.addWidget(self.color_btn)

        left_layout.addLayout(controls_row)

        # action buttons
        btn_row = QHBoxLayout()

        self.convert_btn = QPushButton("Convert to SVG")
        self.convert_btn.clicked.connect(self._on_convert)
        btn_row.addWidget(self.convert_btn)

        self.save_svg_btn = QPushButton("Save SVG...")
        self.save_svg_btn.clicked.connect(self._on_save)
        self.save_svg_btn.setEnabled(False)
        btn_row.addWidget(self.save_svg_btn)

        self.save_png_btn = QPushButton("Save as PNG")
        self.save_png_btn.clicked.connect(self._on_save_png)
        btn_row.addWidget(self.save_png_btn)

        self.save_jpg_btn = QPushButton("Save as JPG")
        self.save_jpg_btn.clicked.connect(self._on_save_jpg)
        btn_row.addWidget(self.save_jpg_btn)

        left_layout.addLayout(btn_row)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: gray;")
        left_layout.addWidget(self.status_label)

        splitter.addWidget(left_panel)

        # ---- Right panel: SVG preview ----
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(QLabel("Preview:"))

        self.svg_widget = QSvgWidget()
        self.svg_widget.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        right_layout.addWidget(self.svg_widget, stretch=1)

        splitter.addWidget(right_panel)
        splitter.setSizes([450, 450])

        # keyboard shortcut: Ctrl+Enter to convert
        self.latex_input.installEventFilter(self)

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------
    def eventFilter(self, obj, event):
        if obj is self.latex_input and event.type() == event.Type.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter) and (event.modifiers() & Qt.ControlModifier):
                self._on_convert()
                return True
        return super().eventFilter(obj, event)

    def _pick_color(self):
        color = QColorDialog.getColor(self._text_color, self, "Choose LaTeX text color")
        if color.isValid():
            self._text_color = color

    # ------------------------------------------------------------------
    # Core actions
    # ------------------------------------------------------------------
    def _on_convert(self):
        latex_expr = self.latex_input.toPlainText().strip()
        if not latex_expr:
            self.status_label.setText("Enter a LaTeX expression first.")
            return

        fontsize = self.fontsize_spin.value()
        color_name = self._text_color.name()  # e.g. "#000000"

        try:
            svg_bytes = latex_to_svg_bytes(latex_expr, fontsize=fontsize, color=color_name)
        except LatexToSvgError as e:
            self.status_label.setText("Conversion failed — see error dialog.")
            QMessageBox.critical(self, "LaTeX Error", str(e))
            return

        self._current_svg_bytes = svg_bytes
        self.svg_widget.load(svg_bytes)
        self.svg_widget.setFixedSize(self.svg_widget.sizeHint())

        self.save_svg_btn.setEnabled(True)
        self.save_png_btn.setEnabled(True)
        self.save_jpg_btn.setEnabled(True)
        self.status_label.setText("Converted successfully.")

    def _on_save(self):
        if self._current_svg_bytes is None:
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save SVG", str(Path.home() / "formula.svg"), "SVG Files (*.svg)"
        )
        if not path:
            return

        try:
            with open(path, "wb") as f:
                f.write(self._current_svg_bytes)
            self.status_label.setText(f"Saved to {path}")
        except OSError as e:
            QMessageBox.critical(self, "Save Error", f"Could not save file: {e}")

    def _on_save_png(self):
        if self._current_svg_bytes is None:
            self.status_label.setText("Convert first!")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save as PNG", str(Path.home() / "formula.png"), "PNG Files (*.png)"
        )
        if not path:
            return

        try:
            # Re-render with PNG format
            latex_expr = self.latex_input.toPlainText().strip()
            if not latex_expr:
                self.status_label.setText("No LaTeX expression to save.")
                return

            fontsize = self.fontsize_spin.value()
            color_name = self._text_color.name()

            png_bytes = latex_to_png_bytes(latex_expr, fontsize=fontsize, color=color_name)

            with open(path, "wb") as f:
                f.write(png_bytes)
            self.status_label.setText(f"Saved as PNG to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Could not save PNG: {e}")

    def _on_save_jpg(self):
        if self._current_svg_bytes is None:
            self.status_label.setText("Convert first!")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save as JPG", str(Path.home() / "formula.jpg"), "JPG Files (*.jpg)"
        )
        if not path:
            return

        try:
            latex_expr = self.latex_input.toPlainText().strip()
            if not latex_expr:
                self.status_label.setText("No LaTeX expression to save.")
                return

            fontsize = self.fontsize_spin.value()
            color_name = self._text_color.name()

            jpg_bytes = latex_to_jpg_bytes(latex_expr, fontsize=fontsize, color=color_name)

            with open(path, "wb") as f:
                f.write(jpg_bytes)
            self.status_label.setText(f"Saved as JPG to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Could not save JPG: {e}")

def main():
    app = QApplication(sys.argv)
    window = LatexToSvgWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()