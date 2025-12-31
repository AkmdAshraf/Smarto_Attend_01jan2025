import requests
import os
import json

BASE_URL = "http://127.0.0.1:5000"
STUDENTS_FILE = "Smarto_Attend/students.json"
DATASET_DIR = "Smarto_Attend/dataset"

def verify():
    print("Starting Verification...")
    
    # 1. Add Student
    print("1. Adding Student...")
    payload = {"roll_no": "999", "name": "VerificationUser"}
    response = requests.post(f"{BASE_URL}/add_student", data=payload)
    
    if response.status_code == 200:
        print("   -> Request Successful")
    else:
        print(f"   -> Request Failed: {response.status_code}")
        return

    # Check JSON
    with open(STUDENTS_FILE, 'r') as f:
        data = json.load(f)
        if "999" in data and data["999"]["name"] == "VerificationUser":
            print("   -> JSON Updated Successfully")
        else:
            print("   -> JSON Update FAILED")
            return

    # Check Folder
    if os.path.exists(os.path.join(DATASET_DIR, "999")):
        print("   -> Dataset Folder Created Successfully")
    else:
        print("   -> Dataset Folder Creation FAILED")
        return

    # 2. List Students
    print("2. Listing Students...")
    response = requests.get(f"{BASE_URL}/students")
    if "VerificationUser" in response.text:
        print("   -> Student found in list")
    else:
        print("   -> Student NOT found in list")
        return

    # 3. Delete Student
    print("3. Deleting Student...")
    response = requests.get(f"{BASE_URL}/delete_student/999") # Note: Using GET as per implementation
    
    # Check JSON
    with open(STUDENTS_FILE, 'r') as f:
        data = json.load(f)
        if "999" not in data:
            print("   -> Student Removed from JSON Successfully")
        else:
            print("   -> Student Removal FAILED")
            return

    # Check Folder
    if not os.path.exists(os.path.join(DATASET_DIR, "999")):
        print("   -> Dataset Folder Removed Successfully")
    else:
        print("   -> Dataset Folder Removal FAILED")
        return

    print("\nALL TESTS PASSED!")

if __name__ == "__main__":
    verify()
