from setuptools import setup
import py2app
import sys
import os

# Streamlit app configuration for py2app
APP = ['main.py']

# Data files to include with the app
DATA_FILES = []

# Options for py2app
OPTIONS = {
    'argv_emulation': False,
    'packages': [
        'streamlit',
        'pandas', 
        'PIL',
        'fitz',
        'numpy',
        'io',
        'base64',
        'logging',
        'struct'
    ],
    'includes': [
        'pdf_analyzer',
        'utils',
        'streamlit.runtime.scriptrunner',
        'streamlit.web.cli',
    ],
    'excludes': [
        'tkinter',
        'matplotlib',
        'jupyter',
        'IPython',
        'pytest'
    ],
    'resources': [],
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
        }
    }
}

setup(
    name='PDF Preflight Tool',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)