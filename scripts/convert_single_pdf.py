import os
import pypdf
import argparse

def convert_single_file(pdf_path, output_path=None):
    if not os.path.exists(pdf_path):
        print(f"Error: File not found - {pdf_path}")
        return

    # Determine output path if not provided
    if output_path is None:
        output_path = os.path.splitext(pdf_path)[0] + ".txt"
    
    # If output_path is a directory, append the filename
    if os.path.isdir(output_path):
        filename = os.path.basename(pdf_path)
        txt_filename = os.path.splitext(filename)[0] + ".txt"
        output_path = os.path.join(output_path, txt_filename)

    print(f"Converting file: {pdf_path}")
    print(f"Output to: {output_path}")

    try:
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print("Success.")
    except Exception as e:
        print(f"Error converting file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a single PDF file to text.")
    parser.add_argument("file_path", help="Path to the PDF file")
    parser.add_argument("--out", help="Output file path or directory (optional)", default=None)
    
    args = parser.parse_args()
    convert_single_file(args.file_path, args.out)
