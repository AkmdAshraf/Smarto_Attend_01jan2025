#!/usr/bin/env python3
"""
Debug Script for Face Recognition Attendance System
Run this to identify issues with ID mapping and recognition accuracy
"""

import os
import json
import cv2
import numpy as np
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STUDENTS_FILE = os.path.join(BASE_DIR, 'students.json')
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
MODEL_FILE = os.path.join(BASE_DIR, 'trained_model.yml')

def load_students():
    """Load students from JSON file"""
    if not os.path.exists(STUDENTS_FILE):
        print("❌ ERROR: students.json not found!")
        return {}
    
    with open(STUDENTS_FILE, 'r') as f:
        try:
            data = json.load(f)
            print(f"✅ Loaded {len(data)} students from students.json")
            return data
        except json.JSONDecodeError:
            print("❌ ERROR: students.json is corrupted or invalid JSON!")
            return {}

def check_id_mapping():
    """Check for ID mapping inconsistencies between dataset and students.json"""
    print("\n" + "="*60)
    print("🔍 CHECKING ID MAPPING BETWEEN DATASET AND STUDENTS.JSON")
    print("="*60)
    
    students = load_students()
    
    # Get all student IDs from students.json
    json_ids = set(students.keys())
    print(f"📄 Students in JSON: {sorted(json_ids)}")
    
    # Get all student IDs from dataset folder
    dataset_ids = set()
    if os.path.exists(DATASET_DIR):
        for item in os.listdir(DATASET_DIR):
            item_path = os.path.join(DATASET_DIR, item)
            if os.path.isdir(item_path):
                dataset_ids.add(item)
    
    print(f"📁 Students in dataset folder: {sorted(dataset_ids)}")
    
    # Find mismatches
    only_in_json = json_ids - dataset_ids
    only_in_dataset = dataset_ids - json_ids
    in_both = json_ids.intersection(dataset_ids)
    
    print("\n📊 MAPPING ANALYSIS:")
    print(f"✅ In both files: {sorted(in_both)}")
    
    if only_in_json:
        print(f"❌ ONLY in JSON (has entry but no photos): {sorted(only_in_json)}")
        for roll_no in only_in_json:
            print(f"   - {roll_no}: {students[roll_no]['name']}")
    
    if only_in_dataset:
        print(f"❌ ONLY in Dataset (has photos but no JSON entry): {sorted(only_in_dataset)}")
        for roll_no in only_in_dataset:
            # Check if folder has images
            folder_path = os.path.join(DATASET_DIR, roll_no)
            images = [f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.png'))]
            print(f"   - {roll_no}: {len(images)} images found")
    
    return students, dataset_ids

def check_dataset_quality():
    """Check quality of dataset images"""
    print("\n" + "="*60)
    print("📸 CHECKING DATASET IMAGE QUALITY")
    print("="*60)
    
    if not os.path.exists(DATASET_DIR):
        print("❌ Dataset directory not found!")
        return {}
    
    quality_report = {}
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    for roll_no in os.listdir(DATASET_DIR):
        folder_path = os.path.join(DATASET_DIR, roll_no)
        if not os.path.isdir(folder_path):
            continue
            
        images = [f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.png'))]
        
        if not images:
            print(f"⚠️  {roll_no}: No images found!")
            quality_report[roll_no] = {"count": 0, "issues": ["No images"]}
            continue
        
        print(f"\n👤 {roll_no}: {len(images)} images")
        quality_report[roll_no] = {"count": len(images), "issues": []}
        
        # Check first few images
        for img_name in images[:5]:  # Check first 5 images
            img_path = os.path.join(folder_path, img_name)
            img = cv2.imread(img_path)
            
            if img is None:
                quality_report[roll_no]["issues"].append(f"{img_name}: Failed to load")
                print(f"   ❌ {img_name}: Failed to load")
                continue
                
            if len(img.shape) == 3:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                gray = img
            
            # Check face detection
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                quality_report[roll_no]["issues"].append(f"{img_name}: No face detected")
                print(f"   ⚠️  {img_name}: No face detected")
            
            # Check image size
            h, w = gray.shape
            if w < 100 or h < 100:
                quality_report[roll_no]["issues"].append(f"{img_name}: Too small ({w}x{h})")
                print(f"   ⚠️  {img_name}: Too small ({w}x{h})")
    
    return quality_report

def check_model():
    """Check if model exists and can be loaded"""
    print("\n" + "="*60)
    print("🤖 CHECKING TRAINED MODEL")
    print("="*60)
    
    if not os.path.exists(MODEL_FILE):
        print("❌ Model file not found! Train the model first.")
        return False
    
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(MODEL_FILE)
        
        # Get model info
        model_info = recognizer.getLabels()
        if model_info is not None:
            unique_ids = np.unique(model_info)
            print(f"✅ Model loaded successfully!")
            print(f"   - Contains {len(unique_ids)} unique IDs")
            print(f"   - IDs in model: {sorted(unique_ids)}")
            
            # Check if IDs match dataset
            dataset_ids = set()
            if os.path.exists(DATASET_DIR):
                for item in os.listdir(DATASET_DIR):
                    item_path = os.path.join(DATASET_DIR, item)
                    if os.path.isdir(item_path):
                        try:
                            dataset_ids.add(int(item))
                        except ValueError:
                            dataset_ids.add(item)
            
            model_ids = set(map(str, unique_ids))
            dataset_ids = set(map(str, dataset_ids))
            
            if model_ids != dataset_ids:
                print(f"❌ MISMATCH between model and dataset!")
                print(f"   - In model but not in dataset: {sorted(model_ids - dataset_ids)}")
                print(f"   - In dataset but not in model: {sorted(dataset_ids - model_ids)}")
            else:
                print(f"✅ Model IDs match dataset IDs!")
                
        return True
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return False

def generate_fix_commands():
    """Generate commands to fix identified issues"""
    print("\n" + "="*60)
    print("🔧 RECOMMENDED FIXES")
    print("="*60)
    
    students, dataset_ids = check_id_mapping()
    
    print("\n📋 STEP-BY-STEP FIXES:")
    
    # 1. Fix ID mismatches
    print("\n1️⃣  FIX ID MISMATCHES:")
    json_ids = set(students.keys())
    only_in_json = json_ids - dataset_ids
    only_in_dataset = dataset_ids - json_ids
    
    if only_in_json:
        print("   For students in JSON but not in dataset:")
        for roll_no in only_in_json:
            print(f"   - Delete from JSON: DELETE /delete_student/{roll_no}")
    
    if only_in_dataset:
        print("\n   For students in dataset but not in JSON:")
        for roll_no in only_in_dataset:
            print(f"   - Add to JSON manually or delete folder:")
            print(f"     Folder to delete: {os.path.join(DATASET_DIR, roll_no)}")
    
    # 2. Retrain model
    print("\n2️⃣  RETRAIN MODEL:")
    print("   - Go to: http://localhost:5000/train")
    print("   - Or run training manually")
    
    # 3. Test recognition
    print("\n3️⃣  TEST RECOGNITION:")
    print("   - Open test page: http://localhost:5000/test_recognition")
    print("   - Check confidence scores (should be < 70 for good matches)")
    
    # 4. Verify training data
    print("\n4️⃣  VERIFY TRAINING DATA QUALITY:")
    print("   - Each student needs 30-50 clear face images")
    print("   - Images should show different angles/expressions")
    print("   - Ensure consistent lighting")

def check_excel_data():
    """Check attendance Excel data format"""
    print("\n" + "="*60)
    print("📊 CHECKING ATTENDANCE DATA FOR EXCEL EXPORT")
    print("="*60)
    
    ATTENDANCE_FILE = os.path.join(BASE_DIR, 'attendance.json')
    
    if not os.path.exists(ATTENDANCE_FILE):
        print("❌ attendance.json not found! No attendance data.")
        return
    
    with open(ATTENDANCE_FILE, 'r') as f:
        try:
            attendance = json.load(f)
            print(f"✅ Loaded attendance data for {len(attendance)} students")
            
            students = load_students()
            
            print("\n📝 ATTENDANCE RECORDS:")
            for roll_no, record in attendance.items():
                name = students.get(roll_no, {}).get("name", "UNKNOWN")
                entry = record.get("entry", "NOT RECORDED")
                exit_ = record.get("exit", "NOT RECORDED")
                duration = record.get("duration", "NOT CALCULATED")
                
                print(f"\n👤 {name} ({roll_no}):")
                print(f"   Entry: {entry}")
                print(f"   Exit: {exit_}")
                print(f"   Duration: {duration}")
                
                # Check data validity
                issues = []
                if entry == "NOT RECORDED":
                    issues.append("No entry time")
                if exit_ == "NOT RECORDED" and entry != "NOT RECORDED":
                    issues.append("Entry but no exit (student still in class?)")
                if duration == "NOT CALCULATED" and entry != "NOT RECORDED" and exit_ != "NOT RECORDED":
                    issues.append("Has entry and exit but no duration calculated")
                
                if issues:
                    print(f"   ⚠️  Issues: {', '.join(issues)}")
                    
        except json.JSONDecodeError:
            print("❌ attendance.json is corrupted!")

def main():
    """Main debugging function"""
    print("🔍 FACE RECOGNITION DEBUGGER")
    print("="*60)
    
    # Check all components
    check_id_mapping()
    check_dataset_quality()
    check_model()
    check_excel_data()
    generate_fix_commands()
    
    print("\n" + "="*60)
    print("✅ DEBUGGING COMPLETE")
    print("="*60)
    
    print("\n📋 QUICK FIX SUMMARY:")
    print("1. Ensure Roll Numbers match exactly between dataset folders and students.json")
    print("2. Train model with at least 30 images per student")
    print("3. Test recognition at: http://localhost:5000/test_recognition")
    print("4. Check confidence scores - should be < 70 for good matches")

if __name__ == "__main__":
    main()
