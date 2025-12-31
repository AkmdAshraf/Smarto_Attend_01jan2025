# SMARTO ATTEND – Anti‑Gravity Web App Prompt (MD File)

> Use this file as a **single source of truth** to generate the entire project from scratch using any AI / Anti‑Gravity / Copilot / Code Generator.

---

## 1. Project Title

**SMARTO ATTEND – Smart Face‑Based Attendance Web Application**

---

## 2. Core Objective

Build a **fully working web application** that:

* Runs on **Windows 10/11**
* Uses **Python + Flask** as backend
* Uses **HTML + CSS** for frontend
* Uses **OpenCV only** for face detection & recognition
* Does **NOT** use `dlib` or `face_recognition`
* Works with **Python 3.11+**

The app must:

* Register students
* Capture student photos from webcam
* Train a face recognition model
* Track **entry & exit time** using camera
* Calculate attendance duration
* Export final attendance to **Excel (.xlsx)**

---

## 3. Technology Constraints (VERY IMPORTANT)

### ✅ Allowed

* Python 3.11+
* Flask
* OpenCV (`opencv-contrib-python` REQUIRED)
* Haar Cascade face detection
* LBPH Face Recognizer
* JSON files for storage
* Pandas + OpenPyXL for Excel export

### ❌ NOT Allowed

* `face_recognition`
* `dlib`
* TensorFlow / PyTorch
* SQL databases
* Cloud services

---

## 4. Folder Structure (MUST FOLLOW)

```
Smarto_Attend/
│
├── app.py
├── students.json
├── attendance.json
├── trained_model.yml
│
├── dataset/
│   └── <roll_no>/
│       ├── img1.jpg
│       ├── img2.jpg
│       └── ...
│
├── static/
│   └── style.css
│
└── templates/
    ├── home.html
    ├── add_student.html
    ├── students.html
    ├── attendance.html
    └── export.html
```

---

## 5. Web Pages & Functional Requirements

### 5.1 Home Page (`/`)

**Purpose:** Main dashboard

**UI Elements:**

* Title: SMARTO ATTEND
* Buttons:

  * Add Student
  * View Students
  * Live Attendance
  * Export Attendance
  * Exit App

---

### 5.2 Add Student Page (`/add_student`)

**Inputs:**

* Roll Number (unique)
* Student Name

**Actions:**

* Open webcam
* Capture **30 face images automatically**
* Store images in `dataset/<roll_no>/`
* Update `students.json`
* Trigger training process

---

### 5.3 Students Page (`/students`)

**Purpose:** CRUD operations

**Features:**

* List all students
* Delete student
* Show roll number & name

---

### 5.4 Training Logic (`/train` – backend route)

**Rules:**

* Automatically trains after new student added
* Uses LBPH Face Recognizer
* Reads images from `dataset/`
* Saves model as `trained_model.yml`

---

### 5.5 Live Attendance Page (`/attendance`)

**Camera Requirements:**

* Live webcam stream
* Draw **vertical virtual line** in center

**Logic:**

* Detect face
* Recognize student using trained model
* Track face X‑coordinate

| Movement     | Action     |
| ------------ | ---------- |
| Left → Right | Entry Time |
| Right → Left | Exit Time  |

---

## 6. Attendance Rules

### Entry & Exit

* Entry time recorded once per student
* Exit time recorded once per student

### Duration

```
Duration = Exit Time − Entry Time
```

### Absent

* If student exists in `students.json`
* But not in `attendance.json`
* Mark as **Absent**

---

## 7. Data Storage Format

### students.json

```json
{
  "101": {"name": "Rahul"},
  "102": {"name": "Anita"}
}
```

### attendance.json

```json
{
  "101": {
    "entry": "09:05:10",
    "exit": "09:55:30",
    "duration": "00:50:20"
  }
}
```

---

## 8. Excel Export (`/export`)

**Output:** `attendance.xlsx`

**Columns:**

1. Roll Number
2. Student Name
3. Entry Time
4. Exit Time
5. Total Duration
6. Status (Present / Absent)
7. Photo Path

---

## 9. UI Design Constraints

* Theme: **Black + Blue**
* Clean layout
* Buttons with hover effects
* Camera on right, controls on left

---

## 10. Development Order (MANDATORY)

1. Flask app runs with `/` route
2. Templates load correctly
3. Student JSON CRUD
4. Webcam capture
5. LBPH training
6. Recognition + attendance logic
7. Excel export

---

## 11. Error‑Handling Rules

* Show friendly messages (not crashes)
* Handle missing model file
* Handle empty dataset
* Prevent duplicate roll numbers

---

## 12. Final Success Criteria

The project is **successful ONLY IF**:

* Runs without errors on Windows
* No 404 pages
* Webcam works inside web app
* Attendance time is accurate
* Excel file is generated correctly

---

## 13. Instruction to AI / Anti‑Gravity

> **Do NOT assume anything**
>
> Ask questions if unclear
>
> Follow this file strictly
>
> Generate COMPLETE working code

---

**END OF PROMPT FILE**
