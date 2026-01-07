Debugging Script to Identify Issues
Save this as debug_face_recognition.py and run it:

python
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
Flask Routes to Add for Debugging
Add these routes to your app.py:

python
# Add after your existing routes

@app.route("/debug")
def debug_page():
    """Debug dashboard"""
    return render_template("debug.html")

@app.route("/api/debug/check_ids")
def api_check_ids():
    """API endpoint to check ID mapping"""
    students = load_students()
    dataset_ids = set()
    
    if os.path.exists(DATASET_DIR):
        for item in os.listdir(DATASET_DIR):
            item_path = os.path.join(DATASET_DIR, item)
            if os.path.isdir(item_path):
                dataset_ids.add(item)
    
    json_ids = set(students.keys())
    
    return {
        "students_in_json": sorted(json_ids),
        "students_in_dataset": sorted(dataset_ids),
        "only_in_json": sorted(json_ids - dataset_ids),
        "only_in_dataset": sorted(dataset_ids - json_ids),
        "in_both": sorted(json_ids.intersection(dataset_ids))
    }

@app.route("/api/debug/fix_mismatch/<action>/<roll_no>")
def api_fix_mismatch(action, roll_no):
    """Fix ID mismatches"""
    if action == "delete_json":
        # Delete from students.json
        students = load_students()
        if roll_no in students:
            del students[roll_no]
            save_students(students)
            return {"status": "success", "message": f"Deleted {roll_no} from students.json"}
    
    elif action == "delete_dataset":
        # Delete from dataset
        folder_path = os.path.join(DATASET_DIR, roll_no)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path, ignore_errors=True)
            return {"status": "success", "message": f"Deleted {roll_no} from dataset"}
    
    return {"status": "error", "message": "Invalid action or roll number"}

@app.route("/api/debug/test_recognition/<roll_no>")
def api_test_recognition(roll_no):
    """Test recognition for specific student"""
    if not os.path.exists(MODEL_FILE):
        return {"status": "error", "message": "Model not trained"}
    
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(MODEL_FILE)
    
    # Test with student's images
    student_folder = os.path.join(DATASET_DIR, str(roll_no))
    if not os.path.exists(student_folder):
        return {"status": "error", "message": "Student folder not found"}
    
    results = []
    images = [f for f in os.listdir(student_folder) if f.endswith('.jpg')][:5]  # Test 5 images
    
    for img_name in images:
        img_path = os.path.join(student_folder, img_name)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            continue
            
        # Preprocess
        from your_main_file import preprocess_face  # Import your function
        img = preprocess_face(img)
        
        # Predict
        id_, confidence = recognizer.predict(img)
        
        results.append({
            "image": img_name,
            "predicted_id": int(id_),
            "expected_id": int(roll_no),
            "confidence": float(confidence),
            "match": int(id_) == int(roll_no) and confidence < 70
        })
    
    return {
        "status": "success",
        "roll_no": roll_no,
        "results": results,
        "accuracy": sum(1 for r in results if r["match"]) / len(results) if results else 0
    }
Debug Template (templates/debug.html)
html
<!DOCTYPE html>
<html>
<head>
    <title>Debug Face Recognition</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; }
        .success { color: green; }
        .error { color: red; }
        .warning { color: orange; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        button { margin: 5px; padding: 8px 16px; }
    </style>
</head>
<body>
    <h1>🔍 Face Recognition Debugger</h1>
    
    <div class="section">
        <h2>1. Check ID Mapping</h2>
        <button onclick="checkIds()">Check ID Mapping</button>
        <div id="id-results"></div>
    </div>
    
    <div class="section">
        <h2>2. Test Recognition</h2>
        <input type="text" id="testRollNo" placeholder="Enter Roll Number">
        <button onclick="testRecognition()">Test Recognition</button>
        <div id="test-results"></div>
    </div>
    
    <div class="section">
        <h2>3. Quick Actions</h2>
        <button onclick="retrainModel()">🔄 Retrain Model</button>
        <button onclick="checkAttendance()">📊 Check Attendance Data</button>
        <button onclick="runFullDebug()">🔧 Run Full Debug</button>
    </div>
    
    <script>
    async function checkIds() {
        const response = await fetch('/api/debug/check_ids');
        const data = await response.json();
        
        let html = `
            <h3>ID Mapping Results:</h3>
            <p>✅ Students in both: ${data.in_both.join(', ') || 'None'}</p>
        `;
        
        if (data.only_in_json.length > 0) {
            html += `<p class="warning">⚠️ Only in JSON (no photos): ${data.only_in_json.join(', ')}</p>`;
        }
        
        if (data.only_in_dataset.length > 0) {
            html += `<p class="error">❌ Only in Dataset (no JSON entry): ${data.only_in_dataset.join(', ')}</p>`;
        }
        
        document.getElementById('id-results').innerHTML = html;
    }
    
    async function testRecognition() {
        const rollNo = document.getElementById('testRollNo').value;
        if (!rollNo) {
            alert('Enter roll number');
            return;
        }
        
        const response = await fetch(`/api/debug/test_recognition/${rollNo}`);
        const data = await response.json();
        
        if (data.status === 'error') {
            document.getElementById('test-results').innerHTML = 
                `<p class="error">${data.message}</p>`;
            return;
        }
        
        let html = `<h3>Recognition Test for ${rollNo}:</h3>`;
        html += `<p>Accuracy: ${(data.accuracy * 100).toFixed(1)}%</p>`;
        html += `<table><tr><th>Image</th><th>Predicted ID</th><th>Confidence</th><th>Match</th></tr>`;
        
        data.results.forEach(result => {
            const matchClass = result.match ? 'success' : 'error';
            html += `
                <tr>
                    <td>${result.image}</td>
                    <td>${result.predicted_id}</td>
                    <td>${result.confidence.toFixed(1)}</td>
                    <td class="${matchClass}">${result.match ? '✅' : '❌'}</td>
                </tr>
            `;
        });
        
        html += '</table>';
        document.getElementById('test-results').innerHTML = html;
    }
    
    async function retrainModel() {
        const response = await fetch('/train');
        if (response.ok) {
            alert('Model training started! Check logs.');
        }
    }
    
    async function checkAttendance() {
        // This would need another API endpoint
        alert('Check terminal/output for attendance data');
    }
    
    function runFullDebug() {
        checkIds();
        // Add more checks as needed
    }
    </script>
</body>
</html>
Prompt for Fixing Excel Data Accuracy
Here's the exact prompt to fix Excel data accuracy:

PROMPT:
"I need to fix my face recognition attendance system. The issues are:

ID Mapping Problem: Roll numbers in dataset folders don't match students.json entries

Recognition Failure: Showing 'Unknown' even for enrolled students

Excel Data Inaccuracy: Attendance times and durations are not accurate

Please fix these by:

First, run the debug script to identify exact ID mismatches between /dataset/ folders and students.json

Fix ID mismatches: Ensure roll numbers match exactly (case-sensitive)

Retrain the model after fixing IDs, using at least 30 images per student

Improve recognition logic: Adjust confidence thresholds and add verification buffers

Fix Excel export: Ensure entry time, exit time, and duration are calculated correctly

Add data validation: Prevent recording attendance outside valid time windows

Specifically for Excel accuracy:

Calculate duration only when both entry AND exit are recorded

Format times consistently (HH:MM:SS)

Include status as 'Present' only if entry was recorded

Add photo path column with correct relative paths

Handle edge cases (no exit time, multiple entries, etc.)"

Steps to Execute:
Save the debug script as debug_face_recognition.py

Run it: python debug_face_recognition.py

Follow the output - it will show exact mismatches

Fix the mismatches using the provided commands

Retrain: Go to http://localhost:5000/train

Test: Use http://localhost:5000/test_recognition