"""
Vision plugin: screenshots and OCR utilities.
- Uses Pillow's ImageGrab for screenshots (`pip install pillow`).
- Uses pytesseract for OCR (`pip install pytesseract`) and requires Tesseract OCR installed on the system.

Functions:
- `take_screenshot(save_path=None)` -> returns saved path or raises RuntimeError
- `ocr_image(path=None, image=None)` -> returns extracted text or instructions if pytesseract missing
- `screenshot_to_text(save_path=None)` -> convenience: screenshot + OCR
"""
from __future__ import annotations
import os
from typing import Optional

try:
    from PIL import Image, ImageGrab
    _PIL_AVAILABLE = True
except Exception:
    _PIL_AVAILABLE = False

try:
    import pytesseract
    _PYTESSERACT_AVAILABLE = True
except Exception:
    _PYTESSERACT_AVAILABLE = False


def _ensure_pillow():
    if not _PIL_AVAILABLE:
        raise RuntimeError("Pillow is not available. Install with: pip install pillow")


def _ensure_pytesseract():
    if not _PYTESSERACT_AVAILABLE:
        raise RuntimeError(
            "pytesseract is not available. Install with: pip install pytesseract and install Tesseract OCR (https://github.com/tesseract-ocr/tesseract)"
        )


def take_screenshot(save_path: Optional[str] = None) -> str:
    """Take a full-screen screenshot and save to `save_path`.

    If `save_path` is None a temporary file `screenshot.png` in the current
    working directory is used. Returns the absolute path to the saved image.
    """
    _ensure_pillow()
    if save_path is None:
        save_path = os.path.join(os.getcwd(), "screenshot.png")
    img = ImageGrab.grab()
    img.save(save_path)
    return os.path.abspath(save_path)


def ocr_image(path: Optional[str] = None, image: Optional["Image.Image"] = None, lang: str = "eng") -> str:
    """Perform OCR on an image file path or a PIL Image object.

    Returns extracted text. Raises RuntimeError with install instructions when
    prerequisites are missing.
    """
    _ensure_pillow()
    _ensure_pytesseract()

    if path is None and image is None:
        raise ValueError("Provide either 'path' or 'image' to perform OCR")

    if path:
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        img = Image.open(path)
    else:
        img = image

    text = pytesseract.image_to_string(img, lang=lang)
    return text.strip()


def screenshot_to_text(save_path: Optional[str] = None, lang: str = "eng") -> str:
    """Take a screenshot and return OCR'd text.

    Convenience wrapper: calls `take_screenshot` then `ocr_image`.
    """
    path = take_screenshot(save_path)
    return ocr_image(path=path, lang=lang)
