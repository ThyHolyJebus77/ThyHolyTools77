**ThyHolyTools77**
Welcome to ThyHolyTools77, a collection of handy utilities for Windows 10. This repository houses a variety of small programs designed to simplify everyday tasks and streamline workflows. While primarily created for Windows 10, they might function on other systems with some adjustments.

**Tools**
*   **Resolution Changer**
  Easily switch between different screen resolutions with this intuitive tool. Perfect for quickly adapting to various displays, such as when remoting in from a phone or tablet.

    **Features:**
    *   Predefined resolution categories (Normal, Tablet, Phone), including percentages of resolutions.
    *   Customizable resolution list.
    *   Add and remove resolutions.
    *   Toggle between single and extended display modes.
    *   Revert to the original resolution.
    *   Temporary resolution change with confirmation.
    *   Settings for revert time.

    **Planned Features:**
    *   Right-click functionality for adjusting resolutions buttons.
    *   Resolution calculator.

*   **FFMPEG-Normalizer**
  Normalize the audio levels of your media files effortlessly. This tool recursively scans a directory and normalizes all specified files according to your preferences.
    **Current Functionality:**
    *   Batch script for normalizing MP3 files.
    *   Adjustable target loudness, bitrate, and other parameters.

    **Planned Features:**
    *   GUI for easy interaction.
    *   Folder selection, bitrate adjustment, and output location settings.
    *   Simplified control over various ffmpeg-normalizer options.

**Usage**
*   **Resolution Changer**
  *   **Requirements:** Python 3.x, `tkinter`, `pywintypes`
    *   Run the `resolution_changer.py` script.
    *   Utilize the GUI to switch between resolutions, add custom resolutions, and adjust settings.

*   **FFMPEG-Normalizer**
  *   **Requirements:** Python 3.x, `ffmpeg_normalize` (install via pip: `pip install ffmpeg_normalize`)
    *   Modify the `ffmpeg_normalizer.bat` script to specify the directory and desired settings.
    *   Run the script to normalize audio files in the specified folder. 

**Contributing**
Contributions are welcome! Feel free to submit bug reports, feature requests, or pull requests.

**Disclaimer**
These tools are provided as-is. While they have been tested on Windows 10, compatibility with other operating systems is not guaranteed. Use them at your own risk.
