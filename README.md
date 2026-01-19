# Zotero Better OCR

**Zero-Config OCR for Zotero 7**

This plugin provides a one-click solution to convert PDF attachments into text notes within Zotero. Unlike other solutions, it comes with **Tesseract OCR** and **Poppler** embedded, requiring no complex installation or system path configuration.

## Features
- **One-Click OCR:** Right-click any PDF -> "Extract Text".
- **Self-Contained:** No need to install Python, Tesseract, or Poppler separately.
- **Privacy First:** Runs entirely offline on your machine.
- **Format Preserving:** Text is saved as a searchable Note attached to the item.
- **Cross-Platform:** Native support for Windows and macOS (Intel & Apple Silicon).

## Installation

1.  Go to the [Releases Page](https://github.com/Lvigentini/zotero-better-ocr/releases).
2.  Download the `.xpi` file matching your operating system:
    -   **Windows:** `BetterOCR_Windows_vX.X.X.xpi`
    -   **macOS:** `BetterOCR_Darwin_vX.X.X.xpi`
3.  Open Zotero -> **Tools** -> **Add-ons**.
4.  Drag and drop the `.xpi` file into the list.
5.  Restart Zotero.

## Usage
1.  Select one or more items (or PDF attachments) in your library.
2.  Right-click and select **Extract Text (Better OCR)**.
3.  Wait for the progress bar to finish.
4.  A new Note will appear attached to the item containing the extracted text.

## Troubleshooting
- **No Menu Item?** Ensure you have restarted Zotero after installation.
- **Errors?** Check `Tools` -> `Developer` -> `Error Console` for logs.
- **Mac Users:** If you see "Unidentified Developer" warnings, you may need to approve the embedded binary in System Settings -> Privacy & Security.
