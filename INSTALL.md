# Install Squeak

Squeak is a standalone desktop app. You do not need Python, a GitHub account,
or access to the source code.

## Choose your download

| Computer | Download |
| --- | --- |
| Mac with an Apple M-series chip | [Squeak for Apple Silicon](https://github.com/karimh97/Squeak/releases/latest/download/Squeak-macOS-Apple-Silicon.zip) |
| Older Mac with an Intel processor | [Squeak for Intel Mac](https://github.com/karimh97/Squeak/releases/latest/download/Squeak-macOS-Intel.zip) |
| Windows 10 or 11 | [Squeak for Windows](https://github.com/karimh97/Squeak/releases/latest/download/Squeak-Windows.zip) |

Not sure which Mac you have? Open the Apple menu and select **About This Mac**.
If **Chip** begins with Apple M, use Apple Silicon. If it says **Processor:
Intel**, use the Intel package.

## Install on macOS

1. Download the appropriate Mac ZIP file from the table above.
2. Double-click the ZIP file to extract `Squeak.app`.
3. Drag `Squeak.app` into the **Applications** folder.
4. The first time you launch it, Control-click `Squeak.app`, select **Open**, and
   then select **Open** again. This extra step is needed while Squeak is unsigned.
5. Allow camera access when macOS asks, if you plan to use live camera input.

After the first launch, open Squeak normally from Applications or Spotlight.

## Install on Windows

1. Download `Squeak-Windows.zip` from the table above.
2. Right-click the ZIP file and select **Extract All**.
3. Keep the entire extracted `Squeak` folder together.
4. Open that folder and double-click `Squeak.exe`.
5. If Windows SmartScreen appears, select **More info**, then **Run anyway**.
   Only do this for a package downloaded from the official Squeak repository.

## Install an update

Squeak 1.1.0 and later checks for new stable releases after launch. When an
update is available, choose **View release** to open the official download page,
**Remind me later**, or **Skip this version**. You can also select **Help > Check
for Updates** at any time.

Download and install the new package using the same steps. On macOS, replace the
old app in Applications. On Windows, replace the old extracted Squeak folder.
Squeak never installs an update silently or forces an update during an active
experiment.

Updating the app does not remove experiment files or preferences. Squeak stores
those separately in the data folder selected during trial setup.
