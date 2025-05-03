"""
image_utils.py

Utility class for image handling, conversion, and preview logic.
Provides reusable helpers for checking image formats, converting EMF/WMF to PNG, and deleting images.
"""

import os

class ImageHandler:
    """
    Utility class for image format checks, conversion, and deletion.
    """
    SUPPORTED_PREVIEW_FORMATS = [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff"]
    UNSUPPORTED_PREVIEW_FORMATS = [".wmf", ".emf"]

    @staticmethod
    def is_supported_for_docx(img_path):
        """
        Checks if the image is supported by python-docx for insertion.

        Args:
            img_path (str): Path to the image file.

        Returns:
            bool: True if supported, False otherwise.
        """
        ext = os.path.splitext(img_path)[1].lower()
        return ext in ImageHandler.SUPPORTED_PREVIEW_FORMATS

    @staticmethod
    def is_supported_for_preview(img_path):
        """
        Checks if the image is supported for direct preview (not WMF/EMF).

        Args:
            img_path (str): Path to the image file.

        Returns:
            bool: True if supported for preview, False otherwise.
        """
        ext = os.path.splitext(img_path)[1].lower()
        return ext not in ImageHandler.UNSUPPORTED_PREVIEW_FORMATS

    @staticmethod
    def convert_emf_to_png(emf_path):
        """
        Converts an EMF/WMF image to PNG for preview using Wand (ImageMagick).

        Args:
            emf_path (str): Path to the EMF/WMF image file.

        Returns:
            str or None: Path to the PNG file if conversion succeeds, else None.
        """
        try:
            from wand.image import Image as WandImage
            png_path = emf_path + ".preview.png"
            if not os.path.exists(png_path):
                # Try both "emf:" and "auto" prefixes for compatibility
                try:
                    with WandImage(filename=f"emf:{emf_path}") as img:
                        img.format = 'png'
                        img.save(filename=png_path)
                except Exception:
                    with WandImage(filename=emf_path) as img:
                        img.format = 'png'
                        img.save(filename=png_path)
            return png_path if os.path.exists(png_path) else None
        except Exception:
            return None

    @staticmethod
    def delete_image_and_preview(img_path):
        """
        Deletes the image file and its PNG preview (if exists).

        Args:
            img_path (str): Path to the image file.
        """
        try:
            if os.path.exists(img_path):
                os.remove(img_path)
            png_preview = img_path + ".preview.png"
            if os.path.exists(png_preview):
                os.remove(png_preview)
        except Exception:
            pass
