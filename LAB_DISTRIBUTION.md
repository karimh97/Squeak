# Maintainer release guide

Lab members should use the links in [INSTALL.md](INSTALL.md). They do not need
Python, the source code, or a GitHub account. The remaining instructions on this
page are for project maintainers publishing a new version.

Unsigned packages are appropriate for early lab evaluation but produce security
warnings. Before broad public distribution, sign and notarize the macOS app and
sign the Windows executable.

## Publish the first release

1. Merge all intended changes into `main` and confirm the tests pass.
2. Confirm `squeak/__init__.py` contains `__version__ = "1.0.0"`.
3. Open the repository's **Releases** page and select **Draft a new release**.
4. Choose **Create new tag**, enter `v1.0.0`, and target `main`.
5. Select **Generate release notes**, then **Publish release**.
6. The release workflow tests Squeak and attaches three packages automatically:
   - `Squeak-macOS-Apple-Silicon.zip`
   - `Squeak-macOS-Intel.zip`
   - `Squeak-Windows.zip`
7. Wait for **Actions > Build release apps** to finish before sharing the release.

The release also includes `SHA256SUMS.txt`, which can be used to verify that a
download has not changed.

## Publish a later update

1. Merge the update into `main`.
2. Increase `__version__` in `squeak/__init__.py`, for example from `1.0.0` to
   `1.0.1`. Update `CITATION.cff` when publishing a citable version.
3. Create and publish a matching release tag, such as `v1.0.1`.
4. Wait for all three packages to appear under the release's **Assets** section.

The workflow stops with an error if the tag and app version do not match. This
prevents a package labeled `v1.0.1` from accidentally containing another app
version.

## Test packages without publishing

Open **Actions > Build release apps > Run workflow**. GitHub builds the same
three packages and keeps them as temporary workflow artifacts without creating
a public release.

## Data and updates

Replacing Squeak does not remove research data or settings. They are stored
separately from the app. Every exported CSV records the Squeak version used for
that trial so analyses remain reproducible after an update.
