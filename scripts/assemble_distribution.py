import os
import shutil
import zipfile
import platform

def assemble():
    script_dir = os.path.dirname(os.path.abspath(__file__)) # zotero-better-ocr/scripts
    root_dir = os.path.dirname(script_dir)                  # zotero-better-ocr
    addon_dir = os.path.join(root_dir, "addon")
    dist_dir = os.path.join(root_dir, "dist")
    
    # Platform Detection
    is_windows = platform.system().lower() == 'windows'
    exe_name = "BetterOCR_Tool.exe" if is_windows else "BetterOCR_Tool"
    
    # 1. Check for the Engine
    exe_source = os.path.join(dist_dir, exe_name)
    
    # Handle Mac .app edge case if PyInstaller makes a bundle
    if not is_windows and not os.path.exists(exe_source):
        # Fallback logic if needed, but --onefile should make a binary
        pass 

    if not os.path.exists(exe_source):
        print(f"ERROR: Engine '{exe_name}' not found in {dist_dir}")
        print("Run 'python scripts/build_exe.py' first.")
        return

    # 2. Define Output XPI name based on platform
    # e.g., BetterOCR_Windows.xpi or BetterOCR_Mac.xpi
    platform_suffix = "Windows" if is_windows else platform.system()
    xpi_name = f"BetterOCR_{platform_suffix}.xpi"
    output_path = os.path.join(root_dir, xpi_name)
    
    print(f"Packaging {xpi_name}...")
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as xpi:
        # Add manifest and bootstrap
        xpi.write(os.path.join(addon_dir, "manifest.json"), "manifest.json")
        xpi.write(os.path.join(addon_dir, "bootstrap.js"), "bootstrap.js")
        
        # Add the binary executable into a 'bin' folder inside the zip
        # IMPORTANT: We rename it to a standard name so bootstrap.js doesn't need to guess
        # Wait, bootstrap.js DOES need to know the name. 
        # Let's keep the platform extension logic in bootstrap.js or standardise here.
        # Standardising to "BetterOCR_Tool" (no extension) on Unix is standard.
        
        archive_path = f"bin/{exe_name}"
        xpi.write(exe_source, archive_path)
        
    print(f"\nSUCCESS! Plugin ready: {output_path}")

if __name__ == "__main__":
    assemble()
