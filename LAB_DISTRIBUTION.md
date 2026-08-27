# Distributing Squeak to the lab

Lab members should not install Python or build Squeak themselves. Give them the
appropriate download from the repository's **Releases** page.

## One-time repository setup

The repository is currently private. Either:

1. Keep it private and add each lab member under **Settings > Collaborators**.
   They will need a GitHub account and must sign in to download releases.
2. Make it public. Anyone with the release link can download Squeak. This is the
   recommended final state for an open-source publication.

## Create a release

1. Confirm the app works locally and all intended changes are on `main`.
2. Open the repository's **Releases** page.
3. Choose **Draft a new release**.
4. Create a new tag such as `v0.1.0` and publish the release.
5. GitHub automatically builds and attaches:
   - `Squeak-macOS-Apple-Silicon.zip` (M1/M2/M3/M4/M5 Macs)
   - `Squeak-macOS-Intel.zip` (older Intel Macs)
   - `Squeak-Windows.zip`

Builds can also be tested without publishing a release from **Actions > Build
release apps > Run workflow**. Those downloads expire, while release downloads
remain available.

## Instructions for lab members

### macOS

1. Download and unzip the Apple Silicon package for M-series Macs, or the Intel
   package for older Macs. Choose **About This Mac** from the Apple menu if the
   processor type is unknown.
2. Drag `Squeak.app` into Applications.
3. On the first launch, macOS may block the unsigned app. Control-click Squeak,
   choose **Open**, then choose **Open** again. Camera permission is requested
   only when a camera trial is used.

### Windows

1. Download and unzip `Squeak-Windows.zip`.
2. Keep the entire extracted `Squeak` folder together.
3. Open the folder and double-click `Squeak.exe`.
4. Windows SmartScreen may warn about the unsigned app. Choose **More info > Run
   anyway** only when the file came from the official Squeak release page.

## Data location

Quick Save writes files to `Documents/Squeak Data` on each computer. Researchers
can also choose a different location when using the explicit export buttons.

## Signing recommendation

Unsigned packages are suitable for a small internal pilot but cause security
warnings. Before broad public distribution:

- macOS: enroll in the Apple Developer Program, sign with a Developer ID
  Application certificate, and notarize the app.
- Windows: obtain an Authenticode code-signing certificate and sign the
  executable/package.

Signing changes how operating systems trust the download; it does not change
Squeak's scoring behavior.
