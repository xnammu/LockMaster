#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import plistlib
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent
DIST_DIR = WORKSPACE / "dist"
BUILD_DIR = WORKSPACE / "build"
ICNS_FILE = WORKSPACE / "LockMaster.icns"
ICON_ICO = WORKSPACE / "icon.ico"
ICON_PNG = WORKSPACE / "icon.png"

def run_cmd(cmd, cwd=WORKSPACE, check=True):
    print(f"--> Running: {' '.join(str(c) for c in cmd)}")
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"STDOUT: {res.stdout}")
        print(f"STDERR: {res.stderr}")
        if check:
            raise RuntimeError(f"Command failed with exit code {res.returncode}: {' '.join(str(c) for c in cmd)}")
    return res

def ensure_icons():
    print("\n[1/5] Checking macOS icons...")
    if not ICON_PNG.exists() and ICON_ICO.exists():
        from PIL import Image
        img = Image.open(ICON_ICO).convert("RGBA")
        img.save(ICON_PNG, "PNG")
        print("Created icon.png from icon.ico")

    if not ICNS_FILE.exists():
        from PIL import Image
        iconset_dir = WORKSPACE / "LockMaster.iconset"
        iconset_dir.mkdir(exist_ok=True)
        img = Image.open(ICON_PNG)
        sizes = [
            (16, "icon_16x16.png"),
            (32, "icon_16x16@2x.png"),
            (32, "icon_32x32.png"),
            (64, "icon_32x32@2x.png"),
            (128, "icon_128x128.png"),
            (256, "icon_128x128@2x.png"),
            (256, "icon_256x256.png"),
            (512, "icon_256x256@2x.png"),
            (512, "icon_512x512.png"),
        ]
        for size, fname in sizes:
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(iconset_dir / fname)
        run_cmd(["iconutil", "-c", "icns", str(iconset_dir), "-o", str(ICNS_FILE)])
        shutil.rmtree(iconset_dir, ignore_errors=True)
        print(f"Created {ICNS_FILE.name}")
    else:
        print(f"Found existing {ICNS_FILE.name}")

def build_app():
    print("\n[2/5] Building LockMaster.app with PyInstaller...")
    pyinstaller_bin = WORKSPACE / ".venv" / "bin" / "pyinstaller"
    if not pyinstaller_bin.exists():
        pyinstaller_bin = "pyinstaller"

    pyinstaller_cmd = [
        str(pyinstaller_bin),
        "--noconfirm",
        "--windowed",
        "--name", "LockMaster",
        "--icon", str(ICNS_FILE),
        "--add-data", f"{WORKSPACE / 'secret.key'}:.",
        "--add-data", f"{ICON_PNG}:.",
        "--osx-bundle-identifier", "com.navneetsingh.lockmaster",
        str(WORKSPACE / "LockMaster.py"),
    ]
    run_cmd(pyinstaller_cmd)

    app_path = DIST_DIR / "LockMaster.app"
    if not app_path.exists():
        raise RuntimeError("LockMaster.app was not created by PyInstaller!")

    print(f"Successfully generated: {app_path}")
    return app_path

def patch_info_plist(app_path):
    print("\n[3/5] Enhancing Info.plist for Retina & macOS integration...")
    plist_path = app_path / "Contents" / "Info.plist"
    if plist_path.exists():
        with open(plist_path, "rb") as f:
            pl = plistlib.load(f)
        pl["NSHighResolutionCapable"] = True
        pl["CFBundleName"] = "LockMaster"
        pl["CFBundleDisplayName"] = "LockMaster"
        pl["CFBundleShortVersionString"] = "1.0.0"
        pl["CFBundleVersion"] = "1.0.0"
        pl["NSHumanReadableCopyright"] = "Copyright © 2026 Navneet Singh. All rights reserved."
        with open(plist_path, "wb") as f:
            plistlib.dump(pl, f)
        print("Updated Info.plist with High-DPI and bundle metadata.")

def create_dmg(app_path):
    print("\n[4/5] Packaging LockMaster.dmg...")
    staging_dir = WORKSPACE / "dmg_staging"
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir()

    # 1. Copy app
    dest_app = staging_dir / "LockMaster.app"
    print(f"Copying {app_path.name} to DMG staging folder...")
    shutil.copytree(app_path, dest_app, symlinks=True)

    # 2. Add /Applications symlink for drag-and-drop installation
    apps_symlink = staging_dir / "Applications"
    os.symlink("/Applications", apps_symlink)

    # 3. Add volume icon
    if ICNS_FILE.exists():
        volume_icon = staging_dir / ".VolumeIcon.icns"
        shutil.copyfile(ICNS_FILE, volume_icon)
        # Set file type and icon attribute if SetFile is available
        setfile_path = shutil.which("SetFile")
        if setfile_path:
            try:
                subprocess.run([setfile_path, "-c", "icnC", str(volume_icon)], capture_output=True)
                subprocess.run([setfile_path, "-a", "C", str(staging_dir)], capture_output=True)
            except Exception:
                pass

    # 4. Create DMG
    dmg_output = DIST_DIR / "LockMaster.dmg"
    if dmg_output.exists():
        dmg_output.unlink()

    hdiutil_cmd = [
        "hdiutil", "create",
        "-volname", "LockMaster",
        "-srcfolder", str(staging_dir),
        "-ov",
        "-format", "UDZO",
        str(dmg_output)
    ]
    run_cmd(hdiutil_cmd)

    # 5. Clean up staging
    shutil.rmtree(staging_dir, ignore_errors=True)
    print(f"DMG successfully created at: {dmg_output}")
    print(f"DMG File Size: {dmg_output.stat().st_size / (1024 * 1024):.2f} MB")
    return dmg_output

def verify_dmg(dmg_path):
    print("\n[5/5] Verifying LockMaster.dmg integrity...")
    # Mount dmg
    # Unmount any existing LockMaster volumes first
    for p in Path("/Volumes").glob("LockMaster*"):
        subprocess.run(["hdiutil", "detach", str(p), "-force"], capture_output=True)

    mount_res = subprocess.run(["hdiutil", "attach", str(dmg_path), "-nobrowse"], capture_output=True, text=True)
    mount_point = None
    for line in mount_res.stdout.splitlines():
        if "/Volumes/" in line:
            mount_point = line[line.find("/Volumes/"):].strip()
            break

    if not mount_point:
        raise RuntimeError(f"Failed to mount DMG for verification:\n{mount_res.stderr}")

    try:
        mounted_path = Path(mount_point)
        app_in_dmg = mounted_path / "LockMaster.app"
        apps_link = mounted_path / "Applications"
        assert app_in_dmg.exists(), "LockMaster.app missing from DMG volume!"
        assert apps_link.exists(), "Applications symlink missing from DMG volume!"
        print(f"DMG verified successfully! Mounted volume contains:")
        print(f" - {app_in_dmg.name}")
        print(f" - {apps_link.name} -> /Applications")
    finally:
        subprocess.run(["hdiutil", "detach", mount_point, "-force"], capture_output=True)
        print("DMG detached cleanly.")

def main():
    print("==========================================")
    print("      LockMaster macOS DMG Builder       ")
    print("==========================================")
    DIST_DIR.mkdir(exist_ok=True)
    ensure_icons()
    app = build_app()
    patch_info_plist(app)
    dmg = create_dmg(app)
    verify_dmg(dmg)
    print("\n==========================================")
    print("   BUILD COMPLETE: LockMaster.dmg READY   ")
    print(f"   Location: {dmg}")
    print("==========================================")

if __name__ == "__main__":
    main()
