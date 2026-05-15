#!/bin/bash
# Build Squeak as a standalone double-clickable app.
# macOS  -> dist/Squeak.app
# Linux  -> dist/Squeak/Squeak
# Windows-> dist/Squeak/Squeak.exe
#
# After first build, double-click dist/Squeak.app (or drag it into /Applications).

set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "==> Creating virtual environment"
    python3 -m venv .venv
    .venv/bin/python -m pip install --upgrade pip
    .venv/bin/python -m pip install -r requirements.txt
fi

echo "==> Installing PyInstaller (if needed)"
.venv/bin/python -m pip install --quiet pyinstaller

echo "==> Generating icon assets"
.venv/bin/python -m squeak.icon

if [[ "$OSTYPE" == "darwin"* ]] && command -v iconutil >/dev/null 2>&1; then
    echo "==> Building .icns (macOS)"
    iconutil -c icns build_assets/Squeak.iconset -o build_assets/icon.icns
fi

echo "==> Cleaning previous build"
rm -rf build dist

echo "==> Running PyInstaller"
.venv/bin/python -m PyInstaller squeak.spec --noconfirm --clean

echo ""
echo "✓ Build complete."
if [ -d "dist/Squeak.app" ]; then
    echo "  → dist/Squeak.app  (drag into /Applications, or double-click to launch)"
elif [ -f "dist/Squeak/Squeak.exe" ]; then
    echo "  → dist/Squeak/Squeak.exe"
else
    echo "  → dist/Squeak/Squeak"
fi
