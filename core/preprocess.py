from io import BytesIO
from PIL import Image, ImageOps

def make_ocr_ready(image: Image.Image) -> Image.Image:
    """Lightweight preprocessing: grayscale + autocontrast + simple threshold."""
    print("Applying lightweight preprocessing (Pillow) for OCR...")
    gray = ImageOps.grayscale(image)
    gray = ImageOps.autocontrast(gray)
    threshold = 160
    bw = gray.point(lambda p: 255 if p > threshold else 0, mode="1")
    return bw.convert("L")

def preprocess_text(image_bytes: bytes) -> bytes:
    """Takes raw image bytes, runs preprocessing, and returns processed image bytes."""
    try:
        with Image.open(BytesIO(image_bytes)) as img:
            processed_img = make_ocr_ready(img)
            buf = BytesIO()
            processed_img.save(buf, format="PNG")
            print("Image preprocessing successful.")
            return buf.getvalue()
    except Exception as e:
        print(f"Error in preprocessing: {e}")
        return image_bytes