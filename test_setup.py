#!/usr/bin/env python3
"""
Quick test script to verify browser automation setup.
This script checks if dependencies are installed and the server is accessible.
"""

import sys
import subprocess
import urllib.request
import urllib.error

def check_dependencies():
    """Check if required packages are installed."""
    print("Checking dependencies...")
    try:
        import selenium
        import webdriver_manager
        print(f"✅ Selenium {selenium.__version__} installed")
        print(f"✅ webdriver-manager installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Run: pip install -r requirements.txt")
        return False

def check_server():
    """Check if the web server is running."""
    print("\nChecking if server is running...")
    try:
        response = urllib.request.urlopen("http://localhost:8000/test_page.html", timeout=2)
        if response.status == 200:
            print("✅ Server is running and accessible")
            return True
        else:
            print(f"❌ Server returned status code: {response.status}")
            return False
    except urllib.error.URLError:
        print("❌ Server is not running")
        print("   Start it with: cd websites/simple-form && python server.py")
        return False

def main():
    print("=" * 50)
    print("Browser Automation Setup Test")
    print("=" * 50)
    
    deps_ok = check_dependencies()
    server_ok = check_server()
    
    print("\n" + "=" * 50)
    if deps_ok and server_ok:
        print("✅ All checks passed! Ready to run automation.")
        print("\nTo test automation, run:")
        print("  cd automations/simple-form")
        print("  python example_automation.py")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()

