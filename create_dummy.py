import cv2
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, 'Smarto_Attend', 'dataset')
ROLL = "9999"

def create_dummy_data():
    roll_dir = os.path.join(DATASET_DIR, ROLL)
    os.makedirs(roll_dir, exist_ok=True)
    
    print(f"Creating dummy images in {roll_dir}...")
    
    # Create 5 dummy grayscale images
    for i in range(1, 6):
        # Create a black image
        img = np.zeros((100, 100), dtype=np.uint8)
        # Draw a white rectangle to make it "unique"
        cv2.rectangle(img, (10+i*5, 10+i*5), (50+i*5, 50+i*5), (255), -1)
        
        file_path = os.path.join(roll_dir, f"{i}.jpg")
        cv2.imwrite(file_path, img)
        
    print("Dummy data created.")

if __name__ == "__main__":
    create_dummy_data()
