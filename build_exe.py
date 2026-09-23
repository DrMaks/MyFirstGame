"""
Automated PyInstaller Build Script.
Compiles Pixel Rogue into a standalone Windows executable ready for Steam deployment.
"""

import os
import sys
import shutil
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")
BUILD_DIR = os.path.join(PROJECT_ROOT, "build")


def build():
    print("=" * 60)
    print("Building Pixel Rogue Standalone Windows Executable...")
    print("=" * 60)

    # Clean old build artifacts if present
    if os.path.exists(DIST_DIR):
        print(f"Cleaning existing dist directory: {DIST_DIR}")
        shutil.rmtree(DIST_DIR)
    if os.path.exists(BUILD_DIR):
        print(f"Cleaning existing build directory: {BUILD_DIR}")
        shutil.rmtree(BUILD_DIR)

    # PyInstaller command
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--name=PixelRogue",
        "--noconsole",           # Windowed app without terminal popup
        "--onedir",              # Clean folder distribution (standard for Steam games)
        "--add-data=steam_appid.txt;.",
        os.path.join(PROJECT_ROOT, "main.py")
    ]

    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)

    if result.returncode == 0:
        # Copy steam_appid.txt to the dist output folder
        target_dir = os.path.join(DIST_DIR, "PixelRogue")
        shutil.copy2(os.path.join(PROJECT_ROOT, "steam_appid.txt"), os.path.join(target_dir, "steam_appid.txt"))
        print("\n" + "=" * 60)
        print("BUILD SUCCESSFUL!")
        print(f"Standalone game folder: {target_dir}")
        print(f"Executable: {os.path.join(target_dir, 'PixelRogue.exe')}")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print(f"BUILD FAILED with exit code {result.returncode}")
        print("=" * 60)


if __name__ == "__main__":
    build()
