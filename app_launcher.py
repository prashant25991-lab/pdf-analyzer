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
import socket
from pathlib import Path

# Add the app directory to Python path
# Use RESOURCEPATH for py2app bundled apps, fallback to file location
resource_path = os.environ.get('RESOURCEPATH')
if resource_path:
    app_dir = Path(resource_path)
else:
    app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

def find_free_port():
    """Find a free port to run Streamlit on"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def start_streamlit():
    """Start the Streamlit server"""
    try:
        # Try default port first, then find free port
        preferred_ports = [8501, 8502, 8503]
        port = None
        
        for p in preferred_ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', p))
                    port = p
                    break
            except OSError:
                continue
        
        if port is None:
            port = find_free_port()
        
        # Import after path is set
        import streamlit.web.cli as stcli
        
        # Streamlit arguments
        sys.argv = [
            "streamlit",
            "run", 
            str(app_dir / "main.py"),
            f"--server.port={port}",
            "--server.address=localhost",
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
            "--server.enableCORS=false",
            "--server.enableXsrfProtection=false"
        ]
        
        # Start browser opening in background
        browser_thread = threading.Thread(
            target=lambda: (time.sleep(3), webbrowser.open(f'http://localhost:{port}')), 
            daemon=True
        )
        browser_thread.start()
        
        print(f"Starting PDF Preflight Tool on port {port}...")
        stcli.main()
        
    except Exception as e:
        print(f"Error starting Streamlit: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

def main():
    """Main application entry point"""
    start_streamlit()

if __name__ == "__main__":
    main()