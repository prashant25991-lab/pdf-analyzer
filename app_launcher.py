#!/usr/bin/env python3
"""
App launcher for PDF Preflight Tool
This script starts the Streamlit app in a way suitable for packaging
"""

import sys
import os
import threading
import time
import webbrowser
import subprocess
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

def start_streamlit():
    """Start the Streamlit server"""
    try:
        # Import after path is set
        import streamlit.web.cli as stcli
        
        # Streamlit arguments
        sys.argv = [
            "streamlit",
            "run", 
            str(app_dir / "main.py"),
            "--server.port=8501",
            "--server.address=localhost",
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
            "--server.enableCORS=false",
            "--server.enableXsrfProtection=false"
        ]
        
        stcli.main()
        
    except Exception as e:
        print(f"Error starting Streamlit: {e}")
        sys.exit(1)

def open_browser():
    """Open browser after server starts"""
    time.sleep(3)  # Wait for server to start
    webbrowser.open('http://localhost:8501')

def main():
    """Main application entry point"""
    print("Starting PDF Preflight Tool...")
    
    # Start browser opening in background
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Start Streamlit (this blocks)
    start_streamlit()

if __name__ == "__main__":
    main()