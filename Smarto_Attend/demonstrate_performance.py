import cv2
import numpy as np
import os
import sys

# Add current directory to path to ensure imports work if run directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logger_config import trace_performance, logger

# Initialize Face Detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

@trace_performance
def process_frame(frame):
    """
    Simulates a Haar Cascade detection task.
    """
    if frame is None:
        logger.error("Received None frame!")
        return
        
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    # Simulate drawing rectangles
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    
    return len(faces)

def run_demo():
    print("Running Trace Performance Demo...")
    
    # Create a dummy image with a white square (simulating basic features)
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(dummy_frame, (150, 150), (350, 350), (255, 255, 255), -1)
    
    # Run the decorated function
    num_faces = process_frame(dummy_frame)
    
    print(f"Demo function executed. Faces detected: {num_faces}")
    print("Check app.log for performance traces.")

if __name__ == "__main__":
    run_demo()
