import cv2
import numpy as np
import easyocr
from ultralytics import YOLO
import os
from PIL import Image
import re

class ANPRProcessor:
    def __init__(self):
        # Load YOLO model for number plate detection
        model_path = os.path.join(os.path.dirname(__file__), "ANPR_Model_Full", "weights", "best.pt")
        self.yolo_model = YOLO(model_path)
        
        # Don't initialize EasyOCR immediately - delay until needed
        self.reader = None
        self.ocr_available = None  # None = not yet tried, True/False = result
    
    def _init_ocr(self):
        """Initialize EasyOCR reader only when needed"""
        if self.ocr_available is None:  # Only try once
            try:
                self.reader = easyocr.Reader(['en'])
                self.ocr_available = True
                print("✅ EasyOCR initialized successfully!")
            except Exception as e:
                print(f"❌ EasyOCR initialization failed: {e}")
                self.reader = None
                self.ocr_available = False
    
    def detect_and_crop_plate(self, image_path: str) -> tuple:
        """
        Detect number plate using YOLO and crop it
        Returns: (cropped_image, original_image_with_bbox)
        """
        # Read image
        original_image = cv2.imread(image_path)
        if original_image is None:
            raise ValueError("Could not read image")
        
        # Run YOLO detection
        results = self.yolo_model(original_image)
        
        # Create a copy for drawing bounding box
        image_with_bbox = original_image.copy()
        
        # Get the first detection (assuming it's the number plate)
        if len(results[0].boxes) > 0:
            # Get bounding box coordinates
            box = results[0].boxes[0]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            # Draw bounding box on original image
            cv2.rectangle(image_with_bbox, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image_with_bbox, "Number Plate", (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            # Crop the number plate
            cropped_plate = original_image[y1:y2, x1:x2]
            
            return cropped_plate, image_with_bbox
        else:
            raise ValueError("No number plate detected in the image")
    
    def extract_text_from_plate(self, plate_image) -> str:
        """
        Extract text from cropped number plate using EasyOCR
        Returns: cleaned number plate text (no spaces)
        """
        # Initialize OCR only when needed
        self._init_ocr()
        
        if not self.ocr_available:
            return "OCR_UNAVAILABLE"
        
        # Convert BGR to RGB for EasyOCR
        if len(plate_image.shape) == 3:
            plate_rgb = cv2.cvtColor(plate_image, cv2.COLOR_BGR2RGB)
        else:
            plate_rgb = plate_image
        
        # Use EasyOCR to extract text
        results = self.reader.readtext(plate_rgb)
        
        if not results:
            return ""
        
        # Get the text with highest confidence
        best_result = max(results, key=lambda x: x[2])
        extracted_text = best_result[1]
        
        # Clean the text: remove spaces and convert to uppercase
        cleaned_text = re.sub(r'[^A-Z0-9]', '', extracted_text.upper())
        
        return cleaned_text
    
    def process_image(self, image_path: str) -> dict:
        """
        Complete ANPR processing: detect, crop, and extract text
        Returns: dict with number_plate, bbox_image, and cropped_plate
        """
        try:
            # Detect and crop number plate
            cropped_plate, bbox_image = self.detect_and_crop_plate(image_path)
            
            # Extract text from cropped plate
            number_plate = self.extract_text_from_plate(cropped_plate)
            
            return {
                "success": True,
                "number_plate": number_plate,
                "bbox_image": bbox_image,
                "cropped_plate": cropped_plate
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def convert_cv2_to_pil(self, cv2_image):
        """Convert OpenCV image to PIL Image for Streamlit display"""
        cv2_image_rgb = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(cv2_image_rgb)
        return pil_image
