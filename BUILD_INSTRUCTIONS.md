# Building PDF Preflight Tool as macOS DMG

This document explains how to build the PDF Preflight Tool as a macOS DMG file for easy distribution and offline use.

## Prerequisites

- macOS computer (Intel or Apple Silicon)
- Python 3.11 or later
- Xcode Command Line Tools (`xcode-select --install`)

## Quick Build Instructions

### Option 1: Local Build on macOS

1. **Clone/Download the project files** to your Mac
2. **Open Terminal** and navigate to the project directory
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Build the app bundle**:
   ```bash
   python setup.py py2app
   ```
5. **Create the DMG**:
   ```bash
   dmgbuild -s dmg_settings.py "PDF Preflight Tool" "PDF-Preflight-Tool.dmg"
   ```

That's it! You'll have a `PDF-Preflight-Tool.dmg` file ready to share.

### Option 2: Using GitHub Actions (Automated)

If you have a GitHub account:

1. **Fork this repository** or upload the files to a new GitHub repository
2. **Enable GitHub Actions** in your repository settings
3. **Push to main branch** - this will automatically trigger the build
4. **Download the DMG** from the Actions artifacts once the build completes

## Installation & Usage

1. **Open the DMG file** by double-clicking
2. **Drag "PDF Preflight Tool"** to the Applications folder
3. **Launch the app** from Applications or Launchpad
4. The app will automatically:
   - Start the PDF analysis server
   - Open your default web browser
   - Show the PDF Preflight Tool interface

## Features of the Packaged App

✅ **Runs completely offline** - no internet connection needed  
✅ **Self-contained** - includes all dependencies  
✅ **Professional interface** - custom styled Streamlit UI  
✅ **PDF analysis** - DPI, color space, print quality checks  
✅ **Multiple file support** - analyze multiple PDFs at once  
✅ **Detailed reporting** - comprehensive analysis results  

## Troubleshooting

### "App cannot be opened" (Security)
- Right-click the app → "Open" → "Open" again
- Or: System Preferences → Security → Allow anyway

### App doesn't start
- Check that Python 3.11+ is available on the system
- Look for error messages in Console.app

### Browser doesn't open automatically  
- Manually navigate to `http://localhost:8501` (or the port shown in the terminal)

## Technical Details

The DMG contains:
- **PDF Preflight Tool.app** - Complete macOS application bundle
- **All dependencies** - Streamlit, PyMuPDF, Pillow, Pandas bundled inside
- **Launcher script** - Starts server and opens browser automatically

The app uses:
- **py2app** for creating the macOS bundle
- **dmgbuild** for creating the installer DMG
- **Streamlit** for the web-based interface
- **PyMuPDF** for PDF analysis

## File Structure

```
PDF Preflight Tool/
├── main.py              # Main Streamlit application
├── pdf_analyzer.py      # PDF analysis logic
├── utils.py             # Utility functions
├── app_launcher.py      # App startup script  
├── setup.py             # py2app configuration
├── dmg_settings.py      # DMG creation settings
├── requirements.txt     # Python dependencies
└── .github/workflows/   # GitHub Actions build script
```

Enjoy sharing your professional PDF analysis tool! 🚀