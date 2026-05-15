"""Squeak app icon — programmatic generator.

Run as a module to write PNG assets to build_assets/:
    python -m squeak.icon
"""

import sys
from pathlib import Path

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QIcon,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)


def render_icon(size: int) -> QImage:
    """Render the Squeak icon at the given square pixel size.

    White rounded square with a centered black "S" and a small pink
    accent dot in the bottom-right echoing the "." from the wordmark.
    A faint 1-px outline gives the icon a defined edge on light
    backgrounds.
    """
    img = QImage(size, size, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    p.setRenderHint(QPainter.TextAntialiasing)
    p.setRenderHint(QPainter.SmoothPixmapTransform)

    rect = QRect(0, 0, size, size)
    radius = size * 0.22

    # Rounded square background — solid white.
    bg_path = QPainterPath()
    bg_path.addRoundedRect(rect, radius, radius)
    p.fillPath(bg_path, QColor("#FFFFFF"))

    # Centered "S" — black, Black weight, slightly tighter spacing.
    font = QFont()
    font.setFamilies(["SF Pro Display", "Helvetica Neue", "Arial Black", "Arial", "DejaVu Sans"])
    font.setPixelSize(int(size * 0.70))
    font.setWeight(QFont.Black)
    font.setLetterSpacing(QFont.PercentageSpacing, 94)
    p.setFont(font)
    p.setPen(QColor("#0A0B0F"))
    # Slight upward bias so the "S" looks optically centered.
    text_rect = QRect(0, int(-size * 0.045), size, size)
    p.drawText(text_rect, Qt.AlignCenter, "S")

    # The "." accent — small pink dot in the bottom-right, hidden at very small sizes.
    if size >= 64:
        dot_d = max(2.0, size * 0.075)
        margin = size * 0.12
        dot_cx = size - margin - dot_d / 2
        dot_cy = size - margin - dot_d / 2
        p.setBrush(QColor("#EC4899"))
        p.setPen(Qt.NoPen)
        p.drawEllipse(int(dot_cx - dot_d / 2), int(dot_cy - dot_d / 2), int(dot_d), int(dot_d))

    # Faint edge so the white icon doesn't disappear on light backgrounds.
    stroke_w = max(1.0, size / 256.0)
    pen = QPen(QColor(0, 0, 0, 28), stroke_w)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)
    # Inset the rect by half the stroke so the line sits inside the rounded shape.
    inset = stroke_w / 2
    p.drawRoundedRect(
        rect.adjusted(int(inset), int(inset), -int(inset), -int(inset)),
        radius - inset, radius - inset,
    )

    p.end()
    return img


def build_icon(default_size: int = 512) -> QIcon:
    """Return a multi-resolution QIcon for runtime use."""
    icon = QIcon()
    for s in (16, 32, 64, 128, 256, 512, 1024):
        if s > default_size * 2:
            continue
        icon.addPixmap(QPixmap.fromImage(render_icon(s)))
    return icon


def main() -> int:
    """Write PNG / iconset assets to build_assets/."""
    from PySide6.QtWidgets import QApplication
    if QApplication.instance() is None:
        QApplication(sys.argv)

    out_dir = Path(__file__).resolve().parent.parent / "build_assets"
    out_dir.mkdir(exist_ok=True)
    iconset = out_dir / "Squeak.iconset"
    iconset.mkdir(exist_ok=True)

    # macOS iconset (Apple naming convention)
    sizes = [16, 32, 64, 128, 256, 512]
    for s in sizes:
        render_icon(s).save(str(iconset / f"icon_{s}x{s}.png"))
        render_icon(s * 2).save(str(iconset / f"icon_{s}x{s}@2x.png"))

    # Standalone PNGs for Windows / Linux / in-app fallback
    render_icon(1024).save(str(out_dir / "icon.png"))
    render_icon(256).save(str(out_dir / "icon_256.png"))

    print(f"Wrote icon assets to: {out_dir}")
    print("On macOS, convert iconset to .icns with:")
    print(f"  iconutil -c icns '{iconset}' -o '{out_dir / 'icon.icns'}'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
