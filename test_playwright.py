#!/usr/bin/env python3
"""
Playwright diagnostic script for Replit.
Run this to test if browser launching works.
"""

import sys
import os
import shutil

def test_playwright():
    print("=" * 60)
    print("PLAYWRIGHT DIAGNOSTIC TEST")
    print("=" * 60)

    # 1. Check Python version
    print(f"\n1. Python version: {sys.version}")

    # 2. Check if playwright is installed
    print("\n2. Checking Playwright installation...")
    try:
        import playwright
        print(f"   Playwright version: {playwright.__version__}")
    except ImportError as e:
        print(f"   ERROR: Playwright not installed: {e}")
        return

    # 3. Check browser paths
    print("\n3. Checking browser paths...")
    cache_path = os.path.expanduser("~/.cache/ms-playwright")
    workspace_cache = "/home/runner/workspace/.cache/ms-playwright"

    for path in [cache_path, workspace_cache]:
        if os.path.exists(path):
            print(f"   Found: {path}")
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                print(f"      - {item} ({'dir' if os.path.isdir(item_path) else 'file'})")
        else:
            print(f"   Not found: {path}")

    # 4. Check system chromium
    print("\n4. Checking system Chromium...")
    for name in ['chromium', 'chromium-browser', 'google-chrome', 'chrome']:
        path = shutil.which(name)
        if path:
            print(f"   Found {name}: {path}")

    # 5. Check glib library
    print("\n5. Checking glib library...")
    glib_path = "/nix/store/syzi2bpl8j599spgvs20xjkjzcw758as-glib-2.84.3/lib/libglib-2.0.so.0"
    if os.path.exists(glib_path):
        print(f"   glib exists: {glib_path}")
        try:
            with open(glib_path, 'rb') as f:
                data = f.read(1024)
                print(f"   glib readable: YES (read {len(data)} bytes)")
        except Exception as e:
            print(f"   glib readable: NO - {e}")
    else:
        print(f"   glib NOT found at: {glib_path}")
        # Try to find glib
        import glob
        glib_files = glob.glob("/nix/store/*/lib/libglib-2.0.so.0")
        if glib_files:
            print(f"   Found glib at: {glib_files[:3]}")

    # 6. Test browser launch
    print("\n6. Testing browser launch...")
    from playwright.sync_api import sync_playwright

    tests = [
        ("Default (headless shell)", lambda p: p.chromium.launch(headless=True)),
        ("Channel chromium", lambda p: p.chromium.launch(headless=True, channel='chromium')),
    ]

    # Check if system chromium exists for executable_path test
    system_chromium = shutil.which('chromium') or shutil.which('chromium-browser')
    if system_chromium:
        tests.append(("System chromium", lambda p: p.chromium.launch(headless=True, executable_path=system_chromium)))

    with sync_playwright() as p:
        for test_name, launch_func in tests:
            print(f"\n   Testing: {test_name}...")
            try:
                browser = launch_func(p)
                print(f"   SUCCESS: {test_name}")

                # Try to take a screenshot
                try:
                    page = browser.new_page()
                    page.goto("data:text/html,<h1>Test</h1>")
                    screenshot = page.screenshot()
                    print(f"   Screenshot: {len(screenshot)} bytes")
                    page.close()
                except Exception as e:
                    print(f"   Screenshot failed: {e}")

                browser.close()
                print(f"   Browser closed successfully")

            except Exception as e:
                print(f"   FAILED: {test_name}")
                print(f"   Error: {e}")

    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_playwright()
