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

echo "==> Cleaning previous build"
rm -rf build dist

echo "==> Running PyInstaller"
PYINSTALLER_CONFIG_DIR="$PWD/.pyinstaller" \
    .venv/bin/python -m PyInstaller squeak.spec --noconfirm --clean

if [[ "$OSTYPE" == "darwin"* ]] && [ -d "dist/Squeak.app" ]; then
    echo "==> Cleaning bundle metadata and applying an ad-hoc signature"
    if xattr -cr dist/Squeak.app 2>/dev/null \
        && codesign --force --deep --sign - dist/Squeak.app; then
        echo "==> Ad-hoc signature applied"
    else
        echo "==> Warning: the app was built, but macOS could not apply an ad-hoc signature." >&2
        echo "    This can happen in cloud-synced folders. Move the project to a local folder and rebuild." >&2
    fi
fi

echo ""
echo "✓ Build complete."
if [ -d "dist/Squeak.app" ]; then
    echo "  → dist/Squeak.app  (drag into /Applications, or double-click to launch)"
elif [ -f "dist/Squeak/Squeak.exe" ]; then
    echo "  → dist/Squeak/Squeak.exe"
else
    echo "  → dist/Squeak/Squeak"
fi
