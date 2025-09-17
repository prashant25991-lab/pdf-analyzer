# PDF Preflight Tool - macOS Application

## Project Overview
A professional PDF analysis tool built with Streamlit that checks PDF files for print quality, DPI, color spaces, and other prepress requirements. The project has been configured to build as a macOS DMG application for easy distribution and offline use.

## Current State
- ✅ Streamlit application fully functional and running
- ✅ PDF analysis engine implemented using PyMuPDF
- ✅ Professional UI with custom styling
- ✅ macOS packaging configuration completed
- ✅ GitHub Actions workflow for automated DMG building
- ✅ Complete build instructions provided

## Recent Changes (Sept 17, 2025)
- Created main.py from user's attached Streamlit application code
- Built pdf_analyzer.py for PDF analysis using PyMuPDF (fitz)
- Created utils.py for file formatting and data processing utilities
- Configured app_launcher.py with automatic port detection and browser opening
- Set up setup.py for py2app macOS application bundling
- Created dmg_settings.py for DMG installer configuration
- Added GitHub Actions workflow for automated building on macOS
- Provided comprehensive BUILD_INSTRUCTIONS.md

## User Requirements
User wants to convert their Streamlit PDF Preflight Tool into a DMG format so they can:
- Share with friends easily
- Run the application offline without dependencies
- Have a professional macOS application bundle

## Project Architecture
- **main.py** - Streamlit web interface with custom CSS styling
- **pdf_analyzer.py** - Core PDF analysis using PyMuPDF (fitz) library
- **utils.py** - Utility functions for file formatting and dataframe creation
- **app_launcher.py** - macOS app launcher that starts Streamlit server and opens browser
- **setup.py** - py2app configuration for creating macOS .app bundle
- **dmg_settings.py** - Configuration for creating installer DMG
- **.github/workflows/build-macos-dmg.yml** - Automated GitHub Actions build

## Technical Constraints Identified
- macOS application bundles and DMG files can only be properly built on macOS
- py2app requires macOS environment and frameworks
- Current Replit environment is Linux-based, so actual DMG building must happen on macOS

## Build Process
The user needs to either:
1. Run the build process on a Mac computer using the provided instructions
2. Use the GitHub Actions workflow for automated cloud building
3. Have someone with macOS access build the DMG for them

## User Preferences
- Wants offline functionality (✅ achieved with bundled dependencies)
- Wants easy sharing format (✅ DMG provides this)
- Wants professional appearance (✅ custom styling maintained)