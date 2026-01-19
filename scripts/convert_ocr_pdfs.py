import os
import argparse
import sys
import shutil

# --- USER CONFIGURATION ---
# Default paths to use if not found in System PATH
DEFAULT_POPPLER_PATH = r"C:\Users\31019232\Downloads\poppler-25.12.0\Library\bin"
DEFAULT_TESSERACT_PATH = r"C:\Users\31019232\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
# --------------------------

try:
    from pdf2image import convert_from_path
    import pytesseract
except ImportError:
    print("Missing libraries. Please install them using:")
    print("pip install pdf2image pytesseract pillow")
    sys.exit(1)

def resolve_tools(poppler_arg, tesseract_arg):
    """
    Determines the correct paths for Poppler and Tesseract by checking:
    1. Command line arguments
    2. System PATH
    3. Hardcoded defaults
    """
    # --- Resolve Poppler ---
    final_poppler = poppler_arg
    if not final_poppler:
        # Check if in PATH
        if shutil.which("pdftoppm"):
            final_poppler = None # pdf2image will find it automatically
        elif os.path.exists(DEFAULT_POPPLER_PATH):
            final_poppler = DEFAULT_POPPLER_PATH
            print(f"[Auto-Config] Using default Poppler: {final_poppler}")
    
    # --- Resolve Tesseract ---
    final_tesseract = tesseract_arg
    if not final_tesseract:
        # Check if in PATH
        if shutil.which("tesseract"):
            final_tesseract = None # pytesseract might find it, but usually safer to set cmd if known
        elif os.path.exists(DEFAULT_TESSERACT_PATH):
            final_tesseract = DEFAULT_TESSERACT_PATH
            print(f"[Auto-Config] Using default Tesseract: {final_tesseract}")
            
    return final_poppler, final_tesseract

def ocr_file(pdf_path, output_path, poppler_path=None, tesseract_path=None):
    print(f"Processing (OCR): {os.path.basename(pdf_path)}...")
    
    # Configure Tesseract
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path, poppler_path=poppler_path)
        
        full_text = ""
        for i, image in enumerate(images):
            text = pytesseract.image_to_string(image)
            full_text += text + "\n"
            print(f"  - Page {i+1} done")
            
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        print(f"Finished: {output_path}")
        return True
    except Exception as e:
        print(f"Error OCR-ing {pdf_path}: {e}")
        err_msg = str(e).lower()
        if "poppler" in err_msg:
            print("\n[ERROR] Poppler not found. Please check the path configuration.")
        elif "tesseract" in err_msg:
            print("\n[ERROR] Tesseract not found. Please check the path configuration.")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apply OCR to a single PDF or a queue file.")
    parser.add_argument("input", help="Path to a PDF file OR a text queue file")
    parser.add_argument("--dest", help="Destination folder for output", default=None)
    parser.add_argument("--poppler", help="Override path to Poppler bin", default=None)
    parser.add_argument("--tesseract", help="Override path to Tesseract exe", default=None)
    
    args = parser.parse_args()
    input_path = args.input
    
    # Resolve tool paths
    poppler_dir, tesseract_cmd = resolve_tools(args.poppler, args.tesseract)

    if not os.path.exists(input_path):
        print(f"Error: Input path not found - {input_path}")
        sys.exit(1)

    # Mode Detection
    if input_path.lower().endswith('.pdf'):
        # --- SINGLE FILE MODE ---
        destination = args.dest if args.dest else os.path.dirname(input_path)
        if not destination: destination = "." 
        
        filename = os.path.basename(input_path)
        txt_filename = os.path.splitext(filename)[0] + ".txt"
        output_path = os.path.join(destination, txt_filename)
        
        ocr_file(input_path, output_path, poppler_path=poppler_dir, tesseract_path=tesseract_cmd)

    else:
        # --- QUEUE MODE ---
        print(f"Processing queue from: {input_path}")
        destination = args.dest if args.dest else os.path.dirname(input_path)
        if not destination: destination = "."
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                files = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"Error reading queue file: {e}")
            sys.exit(1)

        print(f"Found {len(files)} files to OCR.")
        for pdf_path in files:
            if os.path.exists(pdf_path):
                filename = os.path.basename(pdf_path)
                txt_filename = os.path.splitext(filename)[0] + ".txt"
                output_path = os.path.join(destination, txt_filename)
                ocr_file(pdf_path, output_path, poppler_path=poppler_dir, tesseract_path=tesseract_cmd)
            else:
                print(f"Skipping missing file: {pdf_path}")