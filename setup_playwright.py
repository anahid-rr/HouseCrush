#!/usr/bin/env python3
"""
Setup script for Playwright browsers.
Run this script after installing the requirements to download the necessary browsers.
"""

import subprocess
import sys

def install_playwright_browsers():
    """Install Playwright browsers."""
    try:
        print("Installing Playwright browsers...")
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        print("✅ Playwright browsers installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing Playwright browsers: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_playwright_browsers() 