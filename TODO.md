🟢 PHASE 0 – PREPARATION (DO NOT SKIP)
☐ 0.1 Choose Python Version

Use Python 3.11

Do NOT use 3.13

☐ 0.2 Create Project Folder
Smarto_Attend/

☐ 0.3 Create Virtual Environment
python -m venv venv

☐ 0.4 Activate Virtual Environment (Windows)
venv\Scripts\activate

☐ 0.5 Install Required Libraries
pip install flask opencv-contrib-python numpy pandas openpyxl


❗ DO NOT install:

face_recognition

dlib

🟢 PHASE 1 – BASIC FLASK APP (MUST WORK FIRST)
☐ 1.1 Create Folder Structure
Smarto_Attend/
│
├── app.py
├── students.json
├── attendance.json
│
├── static/
│   └── style.css
│
└── templates/
    └── home.html

☐ 1.2 Create app.py

Goal: App must start without error

from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)

☐ 1.3 Create home.html
<!DOCTYPE html>
<html>
<head>
    <title>SMARTO ATTEND</title>
</head>
<body>
    <h1>SMARTO ATTEND</h1>
    <p>Smart Attendance System</p>
</body>
</html>

☐ 1.4 RUN & VERIFY
python app.py


Open:

http://127.0.0.1:5000


✔ Page loads
✔ No errors

🚫 If this fails → STOP & FIX

🟢 PHASE 2 – HOME PAGE NAVIGATION
☐ 2.1 Add Buttons in home.html

Buttons:

Add Student

Manage Students

Live Attendance

Export Excel

Exit

Each button must have a route

☐ 2.2 Create Empty Routes in app.py
@app.route("/add_student")
def add_student():
    return "Add Student Page"

@app.route("/students")
def students():
    return "Students List"

@app.route("/attendance")
def attendance():
    return "Live Attendance"

@app.route("/export")
def export():
    return "Export Excel"


✔ Clicking buttons must NOT show 404

🟢 PHASE 3 – STUDENT CRUD (JSON ONLY)
☐ 3.1 Define students.json Format
{}

☐ 3.2 Add Student Page

Inputs:

Roll Number

Name

Actions:

Save into students.json

Create folder dataset/<roll_no>/

☐ 3.3 Implement CRUD

Add student

View students

Delete student

🚫 NO face recognition yet

🟢 PHASE 4 – FACE CAPTURE (CAMERA ONLY)
☐ 4.1 Open Camera Using OpenCV

Use Haar Cascade

Capture 30 images per student

☐ 4.2 Save Images
dataset/<roll_no>/1.jpg
dataset/<roll_no>/2.jpg
...


✔ Confirm images saved correctly

🟢 PHASE 5 – TRAIN MODEL (LBPH)
☐ 5.1 Load All Face Images

Convert to grayscale

Assign numeric labels (roll numbers)

☐ 5.2 Train LBPH Model
cv2.face.LBPHFaceRecognizer_create()

☐ 5.3 Save Model
trained_model.yml


🚫 Do NOT auto-train on app start

🟢 PHASE 6 – LIVE ATTENDANCE CAMERA
☐ 6.1 Camera Page Layout

Right: Live camera

Left: Logs (Entry / Exit)

☐ 6.2 Draw Vertical Virtual Line

Fixed X coordinate

Visible in camera feed

☐ 6.3 Entry / Exit Logic
Direction	Action
Left → Right	Entry time
Right → Left	Exit time
☐ 6.4 Save Attendance to attendance.json
{
  "1": {
    "entry": "09:05:10",
    "exit": "09:55:30",
    "duration": "00:50:20"
  }
}

🟢 PHASE 7 – TIME WINDOW RULES
☐ 7.1 Set Class Time

Start time (editable)

End time (editable)

☐ 7.2 Only mark attendance inside time window
🟢 PHASE 8 – ABSENT LOGIC

If student in students.json

But NOT in attendance.json
→ Mark Absent

🟢 PHASE 9 – EXCEL EXPORT
☐ 9.1 Generate Excel File

Columns:

Roll Number

Name

Entry Time

Exit Time

Duration

Status (Present/Absent)

Photo Path

☐ 9.2 Save as:
attendance.xlsx

🟢 PHASE 10 – UI STYLING

Black + Blue theme

Hover effects

Two-column layout

Scrollable logs

🔒 HARD CONSTRAINTS (VERY IMPORTANT)

❌ NO assumptions
❌ NO dlib
❌ NO face_recognition
❌ NO background threads without control
❌ NO auto camera on app start

✔ Camera opens ONLY on attendance page
✔ Every route must exist
✔ Every button must work

🎯 FINAL CHECKLIST

✔ App opens
✔ Students can be added
✔ Faces captured
✔ Model trained
✔ Attendance marked
✔ Excel exported