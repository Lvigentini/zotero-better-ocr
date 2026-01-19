# Developer Guide: Building Zotero Better OCR

This guide explains how to compile the Zotero plugin from source. The build process creates a standalone executable (bundling Python, Tesseract, and Poppler) and packages it into a Zotero `.xpi` file.

**Important:** You cannot cross-compile. To build the Windows version, you need a Windows machine. To build the Mac version, you need a Mac.

## Prerequisites
- **Python 3.9+**
- **Git**
- **libs/** folder (Not in Git, you must create this)

---

## 1. Setup the Repository
```bash
git clone git@github.com:Lvigentini/zotero-better-ocr.git
cd zotero-better-ocr
pip install pyinstaller pdf2image pytesseract
```

## 2. Prepare Dependencies (`libs/`)
The build script expects a `libs` folder in the root directory containing the raw binaries for your platform.

### Windows Setup
1.  Create `libs/` folder.
2.  **Poppler:** Download [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases). Extract and place the `Library` folder such that `libs/poppler/Library/bin/pdftoppm.exe` exists.
3.  **Tesseract:** Download [Tesseract installer](https://github.com/UB-Mannheim/tesseract/wiki). Install it, then copy the installation folder to `libs/tesseract`. Ensure `libs/tesseract/tesseract.exe` exists.

### macOS Setup (Apple Silicon & Intel)
1.  Install dependencies via Homebrew: `brew install tesseract poppler`
2.  Create local copies for bundling:
    ```bash
    mkdir -p libs/poppler/bin
    mkdir -p libs/tesseract/bin
    cp $(which pdftoppm) libs/poppler/bin/
    # You may need to copy shared libraries (.dylib) as well using dylibbundler or similar tools if portability is an issue.
    # For Tesseract, copy the binary and the 'tessdata' folder.
    ```

---

## 3. Build the Engine
This compiles the Python logic and the `libs` content into a single executable.

```bash
python scripts/build_exe.py
```
*Output:* `dist/BetterOCR_Tool.exe` (Windows) or `dist/BetterOCR_Tool` (Mac).

## 4. Package the Plugin
This zips the Zotero addon code (`addon/`) along with the generated Engine (`dist/`).

```bash
python scripts/assemble_distribution.py
```
*Output:* `BetterOCR_Windows.xpi` (or `_Darwin.xpi`).

## 5. Release
1.  Create a new Release on GitHub.
2.  Upload the `.xpi` files generated from both Windows and Mac build environments.
