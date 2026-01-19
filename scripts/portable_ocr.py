import os
import sys
import sys
import shutil
import argparse
import subprocess

# --- AUTO-CONFIGURATION LOGIC ---
def get_bundled_paths():
    """
    Returns the paths to Poppler and Tesseract.
    If running as a PyInstaller bundle (frozen), looks inside the temp folder.
    If running as a script, looks for local 'libs' folder or system PATH.
    """
    if getattr(sys, 'frozen', False):
        # We are running inside a bundled .exe
        base_path = sys._MEIPASS
        
        # Windows vs Unix paths
        if os.name == 'nt':
            poppler_path = os.path.join(base_path, 'poppler', 'Library', 'bin')
            tesseract_cmd = os.path.join(base_path, 'tesseract', 'tesseract.exe')
        else:
            # macOS/Linux logic (adjust as needed for specific binary structures)
            poppler_path = os.path.join(base_path, 'poppler', 'bin')
            tesseract_cmd = os.path.join(base_path, 'tesseract', 'bin', 'tesseract')
            
    else:
        # We are running as a normal .py script
        # Check if 'libs' folder exists next to script
        base_path = os.path.dirname(os.path.abspath(__file__))
        local_poppler = os.path.join(base_path, 'libs', 'poppler', 'Library', 'bin')
        local_tesseract = os.path.join(base_path, 'libs', 'tesseract', 'tesseract.exe')
        
        poppler_path = local_poppler if os.path.exists(local_poppler) else None
        tesseract_cmd = local_tesseract if os.path.exists(local_tesseract) else None

    return poppler_path, tesseract_cmd

# Import dependencies
try:
    from pdf2image import convert_from_path
    import pytesseract
except ImportError:
    # If bundled, these should never be missing.
    print("CRITICAL: Missing libraries in bundle.")
    sys.exit(1)

def ocr_file(pdf_path, output_path):
    poppler_dir, tesseract_exe = get_bundled_paths()
    
    # Configure Tesseract
    if tesseract_exe and os.path.exists(tesseract_exe):
        pytesseract.pytesseract.tesseract_cmd = tesseract_exe
        print(f"Using Bundled Tesseract: {tesseract_exe}")
    else:
        # Fallback to system PATH
        print("Using System Tesseract (Bundled not found)")

    # Configure Poppler
    if poppler_dir and os.path.exists(poppler_dir):
        print(f"Using Bundled Poppler: {poppler_dir}")
    else:
        poppler_dir = None # Let pdf2image search PATH
        print("Using System Poppler (Bundled not found)")

    print(f"Processing: {os.path.basename(pdf_path)}")
    try:
        images = convert_from_path(pdf_path, poppler_path=poppler_dir)
        full_text = ""
        for i, image in enumerate(images):
            text = pytesseract.image_to_string(image)
            full_text += text + "\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        print("Success.")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_pdf")
    args = parser.parse_args()
    
    pdf_path = args.input_pdf
    # Default output is same folder, .txt extension
    output_path = os.path.splitext(pdf_path)[0] + ".txt"
    
    ocr_file(pdf_path, output_path)
