import os
import shutil
import zipfile
import platform
import json

def assemble():
    script_dir = os.path.dirname(os.path.abspath(__file__)) 
    root_dir = os.path.dirname(script_dir)                  
    addon_dir = os.path.join(root_dir, "addon")
    dist_dir = os.path.join(root_dir, "dist")
    xpi_dir = os.path.join(root_dir, "xpi")
    
    # Create xpi folder if missing
    if not os.path.exists(xpi_dir):
        os.makedirs(xpi_dir)
    
    # 0. Get Version from Manifest
    manifest_path = os.path.join(addon_dir, "manifest.json")
    with open(manifest_path, 'r') as f:
        data = json.load(f)
        version = data.get('version', '1.0.0')

    # Platform Detection
    is_windows = platform.system().lower() == 'windows'
    exe_name = "BetterOCR_Tool.exe" if is_windows else "BetterOCR_Tool"

    # 1. Check for the Engine
    exe_source = os.path.join(dist_dir, exe_name)
    if not os.path.exists(exe_source):
        print(f"ERROR: Engine '{exe_name}' not found in {dist_dir}")
        print("Run 'python scripts/build_exe.py' first.")
        return

    # 2. Define Output XPI name with Version
    platform_suffix = "Windows" if is_windows else platform.system()
    xpi_name = f"BetterOCR_{platform_suffix}_v{version}.xpi"
    output_path = os.path.join(xpi_dir, xpi_name)

    print(f"Packaging {xpi_name}...")
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as xpi:
        # Add files to Root of Zip
        xpi.write(os.path.join(addon_dir, "manifest.json"), "manifest.json")
        xpi.write(os.path.join(addon_dir, "bootstrap.js"), "bootstrap.js")
        
        # Add Icon
        icon_path = os.path.join(addon_dir, "icon.png")
        if os.path.exists(icon_path):
            xpi.write(icon_path, "icon.png")
        else:
            print("WARNING: icon.png not found in addon folder!")

        # Add Binary
        archive_path = f"bin/{exe_name}"
        xpi.write(exe_source, archive_path)

    print(f"\nSUCCESS! Plugin ready: {output_path}")

if __name__ == "__main__":
    assemble()
