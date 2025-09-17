from setuptools import setup
import py2app
import sys
import os

# Streamlit app configuration for py2app
APP = ['app_launcher.py']

# Data files to include with the app
DATA_FILES = [
    'main.py',
    'pdf_analyzer.py', 
    'utils.py'
]

# Options for py2app
OPTIONS = {
    'argv_emulation': False,
    'packages': [
        'streamlit',
        'pandas', 
        'PIL',
        'fitz',
        'numpy',
        'socket',
        'threading',
        'webbrowser'
    ],
    'includes': [
        'pdf_analyzer',
        'utils',
        'streamlit.web.cli',
        'fitz',
        'PIL.Image'
    ],
    'excludes': [
        'tkinter',
        'matplotlib',
        'jupyter',
        'IPython',
        'pytest',
        'sphinx',
        'docutils'
    ],
    'resources': DATA_FILES,
    'iconfile': None,  # We'll create an icon later
    'plist': {
        'CFBundleName': 'PDF Preflight Tool',
        'CFBundleDisplayName': 'PDF Preflight Tool',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleIdentifier': 'com.pdfpreflighttool.app',
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': True,
        'LSUIElement': False,
        'NSAppTransportSecurity': {
            'NSAllowsArbitraryLoads': True
        },
        'NSAppleEventsUsageDescription': 'This app needs to open your default web browser.'
    }
}

setup(
    name='PDF Preflight Tool',
    app=APP,
    data_files=[],  # Resources handled by py2app options
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)