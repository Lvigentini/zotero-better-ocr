# Developer Guide: Building Zotero Better OCR

This guide explains the architecture and build process for the Zotero plugin.

## Architecture
The plugin consists of two parts:
1.  **The Engine (Python):** A script (`portable_ocr.py`) compiled into a standalone executable using PyInstaller. It bundles Tesseract and Poppler binaries.
2.  **The Addon (JavaScript):** A Zotero Bootstrap extension that executes the bundled engine via `nsIProcess`.

## Development Setup

### Prerequisites
- **Python 3.9+**
- **Git**
- **Node.js** (Optional, only if using other tools)

### Directory Structure
- `addon/`: Zotero plugin source (`bootstrap.js`, `manifest.json`).
- `scripts/`: Python build tools.
- `libs/`: **(Local Only)** Folder where you place raw Tesseract/Poppler binaries for local building.

---

## Building Locally (Manual)

If you want to build the plugin on your own machine (e.g., for testing):

1.  **Prepare Libs:**
    -   Create `libs/poppler` and `libs/tesseract`.
    -   Download/copy the respective binaries for your OS into these folders.
    -   *See `scripts/build_exe.py` logic for expected paths.*

2.  **Build Engine:**
    ```bash
    pip install pyinstaller pdf2image pytesseract
    python scripts/build_exe.py
    ```

3.  **Package XPI:**
    ```bash
    python scripts/assemble_distribution.py
    ```

---

## Release Process (Automated)

We use **GitHub Actions** to automatically build for both Windows and macOS whenever a tag is pushed.

### Steps to Release:

1.  **Bump Version:**
    Update `addon/manifest.json`. You can use the helper:
    ```bash
    python scripts/bump_version.py patch  # or minor/major
    ```

2.  **Commit & Tag:**
    ```bash
    git add addon/manifest.json
    git commit -m "Release v1.0.5"
    git tag v1.0.5
    git push origin v1.0.5
    ```

3.  **Wait for CI:**
    -   Go to the [Actions Tab](https://github.com/Lvigentini/zotero-better-ocr/actions).
    -   Watch the "Build and Release" workflow.
    -   It will spin up Windows and Mac runners, download dependencies, build the XPIs, and draft a release.

4.  **Publish:**
    -   Go to [Releases](https://github.com/Lvigentini/zotero-better-ocr/releases).
    -   Edit the drafted release, check the notes, and click **Publish**.
