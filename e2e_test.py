import requests
import os
import json
import cv2
import numpy as np
import shutil

BASE_URL = "http://127.0.0.1:5000"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STUDENTS_FILE = os.path.join(BASE_DIR, "Smarto_Attend", "students.json")
DATASET_DIR = os.path.join(BASE_DIR, "Smarto_Attend", "dataset")
MODEL_FILE = os.path.join(BASE_DIR, "Smarto_Attend", "trained_model.yml")

TEST_ROLL = "E2E_001"
TEST_NAME = "E2E User"

def setup():
    print("--- Setting up E2E Test ---")
    # Clean up previous test data
    if os.path.exists(STUDENTS_FILE):
        with open(STUDENTS_FILE, 'r') as f:
            data = json.load(f)
        if TEST_ROLL in data:
            del data[TEST_ROLL]
            with open(STUDENTS_FILE, 'w') as f:
                json.dump(data, f, indent=4)
            print("   -> Cleaned json")

    dataset_path = os.path.join(DATASET_DIR, TEST_ROLL)
    if os.path.exists(dataset_path):
        shutil.rmtree(dataset_path)
        print("   -> Cleaned dataset folder")
        
    if os.path.exists(MODEL_FILE):
        try:
            import stat
            os.chmod(MODEL_FILE, stat.S_IWRITE)
            os.remove(MODEL_FILE)
            print("   -> Removed existing model file")
        except Exception as e:
            print(f"   -> Warning: Could not remove model file: {e}. Will check timestamp update instead.")

def run_test():
    print("\n--- Running E2E Test ---")
    
    start_time = os.path.getmtime(MODEL_FILE) if os.path.exists(MODEL_FILE) else 0
    
    # 1. Add Student
    print("1. Adding Student...")
    payload = {"roll_no": TEST_ROLL, "name": TEST_NAME}
    response = requests.post(f"{BASE_URL}/add_student", data=payload)
    
    if response.status_code == 200:
        print("   -> Add Student Request Successful")
    else:
        print(f"   -> FAILED: {response.status_code}")
        return

    # Verify JSON
    with open(STUDENTS_FILE, 'r') as f:
        data = json.load(f)
    if TEST_ROLL in data:
        print("   -> Student found in JSON")
    else:
        print("   -> Student NOT found in JSON. FAILED.")
        return

    # 2. Simulate Capture (Since we can't use webcam in script)
    # The /add_student route creates the folder, so we just populate it.
    print("2. Simulating Face Capture (Generating images)...")
    dataset_path = os.path.join(DATASET_DIR, TEST_ROLL)
    if not os.path.exists(dataset_path):
        print("   -> Dataset folder was NOT created by app. FAILED.")
        return
        
    for i in range(1, 11): # Generates 10 images
        img = np.zeros((100, 100), dtype=np.uint8)
        # Draw something unique based on ID to simulate 'features'
        cv2.circle(img, (50, 50), i*3, (255), 2)
        cv2.imwrite(os.path.join(dataset_path, f"{i}.jpg"), img)
    print("   -> 10 dummy images created.")

    # 3. Train Model
    print("3. Triggering Training...")
    response = requests.get(f"{BASE_URL}/train")
    if response.status_code == 200:
        print("   -> Train Request Successful")
    else:
        print(f"   -> Train Request FAILED with {response.status_code}")
        return

    # 4. Verify Model
    print("4. Verifying Trained Model...")
    if os.path.exists(MODEL_FILE):
        new_time = os.path.getmtime(MODEL_FILE)
        size = os.path.getsize(MODEL_FILE)
        print(f"   -> Model file exists. Size: {size} bytes")
        
        if new_time > start_time:
             print("   -> Model file was UPDATED. Success.")
        else:
             print("   -> Model file was NOT updated. Failed.")
             
        if size > 1000:
            print("   -> Model size seems valid.")
        else:
            print("   -> Model file too small? Warning.")
    else:
        print("   -> Model file NOT found. FAILED.")
        return

    print("\n[SUCCESS] E2E Test Completed Successfully!")

if __name__ == "__main__":
    setup()
    run_test()
