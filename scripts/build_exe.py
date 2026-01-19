import os
import shutil
import subprocess
import sys
import platform

def build():
    # 1. Define Paths relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__)) # zotero-better-ocr/scripts
    root_dir = os.path.dirname(script_dir)                  # zotero-better-ocr
    libs_dir = os.path.join(root_dir, "libs")
    dist_dir = os.path.join(root_dir, "dist")
    
    # 2. Platform Detection
    system = platform.system().lower() # 'windows', 'darwin' (mac), 'linux'
    is_windows = system == 'windows'
    
    print(f"Detected Platform: {system.upper()}")

    # 3. Check Ingredients
    poppler_src = os.path.join(libs_dir, "poppler")
    tesseract_src = os.path.join(libs_dir, "tesseract")
    
    tesseract_bin = "tesseract.exe" if is_windows else "tesseract"
    
    if not os.path.exists(poppler_src):
        print("ERROR: 'libs/poppler' folder missing!")
        return

    if not os.path.exists(tesseract_src):
        print("ERROR: 'libs/tesseract' folder missing!")
        return

    # 4. Construct PyInstaller Command
    
    # Separator for --add-data (Windows=';', Unix=':')
    sep = ";" if is_windows else ":"
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--name", "BetterOCR_Tool",
        "--distpath", dist_dir,
        "--workpath", os.path.join(script_dir, "build"),
        "--specpath", script_dir,
        f"--add-data={poppler_src}{sep}poppler",
        f"--add-data={tesseract_src}{sep}tesseract",
        os.path.join(script_dir, "portable_ocr.py")
    ]
    
    # CRITICAL FIX: Only use --windowed on Windows.
    # On Mac, --windowed creates a .app bundle which confuses the assembler/Zotero.
    # We want a raw binary on Mac.
    if is_windows:
        cmd.insert(4, "--windowed")
    
    print(f"Running build with: {sys.executable} -m PyInstaller ...")
    print("This may take a minute...")
    
    try:
        subprocess.check_call(cmd)
        
        # 5. Output Verification
        output_name = "BetterOCR_Tool.exe" if is_windows else "BetterOCR_Tool"
        final_path = os.path.join(dist_dir, output_name)
        
        if os.path.exists(final_path):
            print(f"\nDONE! Your standalone executable is in: {dist_dir}")
            print(f"File: {output_name}")
        else:
            print("\nWARNING: Build finished but expected output file not found.")
                
    except subprocess.CalledProcessError as e:
        print(f"Build Failed: {e}")

if __name__ == "__main__":
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "pyinstaller"])
        
    build()
