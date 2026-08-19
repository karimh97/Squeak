# PyInstaller spec for Squeak. Run via: ./build_app.sh
# Or manually:  pyinstaller squeak.spec --noconfirm --clean

from pathlib import Path

block_cipher = None
ROOT = Path(SPECPATH).resolve()
ICON_ICNS = str(ROOT / "build_assets" / "icon.icns")
ICON_PNG = str(ROOT / "build_assets" / "icon.png")


a = Analysis(
    ["app.py"],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        ("build_assets/icon.png", "build_assets"),
        ("build_assets/icon.icns", "build_assets"),
        ("build_assets/squeak_logo.png", "build_assets"),
        ("build_assets/squeak_logo_black.png", "build_assets"),
        ("build_assets/squeak_logo_white.png", "build_assets"),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "scipy",
        "pandas",
        "PIL",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Squeak",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_ICNS,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="Squeak",
)

# macOS .app bundle
app = BUNDLE(
    coll,
    name="Squeak.app",
    icon=ICON_ICNS,
    bundle_identifier="science.squeak.app",
    version="1.0.0",
    info_plist={
        "CFBundleDisplayName": "Squeak",
        "CFBundleName": "Squeak",
        "CFBundleShortVersionString": "1.0.0",
        "CFBundleVersion": "1.0.0",
        "LSMinimumSystemVersion": "11.0",
        "NSHighResolutionCapable": True,
        "NSCameraUsageDescription":
            "Squeak uses the camera to display live video while you score "
            "rodent object exploration.",
        "NSMicrophoneUsageDescription":
            "Squeak does not record audio.",
        "LSApplicationCategoryType": "public.app-category.education",
    },
)
