import os
import pypdf
import argparse

def convert_folder(source_dir, dest_dir, threshold=1000):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print(f"Created destination directory: {dest_dir}")
        
    files = [f for f in os.listdir(source_dir) if f.lower().endswith('.pdf')]
    print(f"Found {len(files)} PDF files in {source_dir}")

    ocr_queue = []

    for filename in files:
        pdf_path = os.path.join(source_dir, filename)
        txt_filename = os.path.splitext(filename)[0] + ".txt"
        txt_path = os.path.join(dest_dir, txt_filename)
        
        try:
            reader = pypdf.PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            
            # Check for suspicious file length
            if len(text.strip()) < threshold:
                print(f"[WARNING] Very short text extracted ({len(text)} chars): {filename}")
                ocr_queue.append(pdf_path)
            else:
                print(f"Converted: {filename}")

            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(text)
                
        except Exception as e:
            print(f"FAILED: {filename} - {e}")
            ocr_queue.append(pdf_path)

    # Report results
    if ocr_queue:
        queue_file = os.path.join(dest_dir, "ocr_queue.txt")
        print(f"\n" + "!"*60)
        print(f"WARNING: {len(ocr_queue)} files appear to be scanned images or failed extraction.")
        print(f"They have been listed in: {queue_file}")
        print("!"*60)
        
        with open(queue_file, 'w', encoding='utf-8') as f:
            for path in ocr_queue:
                f.write(path + "\n")
    else:
        print("\nAll files converted successfully with sufficient text content.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert folder PDFs to text and detect scan-only files.")
    parser.add_argument("source", help="Source folder containing PDFs")
    parser.add_argument("destination", help="Destination folder for text files")
    parser.add_argument("--threshold", type=int, default=1000, help="Minimum char count to accept (default 1000)")
    
    args = parser.parse_args()
    convert_folder(args.source, args.destination, args.threshold)
