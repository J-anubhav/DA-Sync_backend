import cv2
import numpy as np

def make_ocr_ready(image: np.ndarray) -> np.ndarray:
    """Applies adaptive thresholding to enhance contrast."""
    print("Applying adaptive thresholding to enhance image for OCR...")
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    ocr_ready_image = cv2.adaptiveThreshold(
        src=gray,
        maxValue=255,
        adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        thresholdType=cv2.THRESH_BINARY,
        blockSize=15,
        C=4
    )
    return ocr_ready_image

def preprocess_text(image_bytes: bytes) -> bytes:
    """Takes raw image bytes, runs preprocessing, and returns processed image bytes."""
    try:
        np_arr = np.frombuffer(image_bytes, np.uint8)
        image_cv = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        processed_image_cv = make_ocr_ready(image_cv)
        
        is_success, buffer = cv2.imencode(".png", processed_image_cv)
        if not is_success:
            raise ValueError("Could not encode processed image to bytes.")
        
        print("Image preprocessing successful.")
        return buffer.tobytes()

    except Exception as e:
        print(f"Error in preprocessing: {e}")
        return image_bytes