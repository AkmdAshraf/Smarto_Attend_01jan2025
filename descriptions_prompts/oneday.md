## **PROMPT FOR PERIOD-WISE ATTENDANCE SYSTEM**

```python
"""
IMPLEMENT PERIOD-WISE ATTENDANCE SYSTEM WITH ANTI-GRAVITY LOGGING

REQUIREMENTS:
1. Configurable daily schedule with multiple periods
2. Each period has: period_name, start_time, end_time, duration, subject, teacher
3. CRUD operations for periods (Create, Read, Update, Delete)
4. Real-time attendance tracking per period with entry/exit times
5. Automatic detection of student movements between periods
6. Break tracking (when students leave/return)
7. Period-wise attendance reports
8. Daily consolidated Excel report with per-period details
9. Period transition logic with grace periods
10. Student presence duration calculation per period

IMPLEMENTATION DETAILS:
- Create periods.json to store period configurations
- Modify attendance.json to store period-wise attendance data
- Add period management interface (admin only)
- Enhance face recognition to track period transitions
- Add real-time period display on attendance page
- Create period-wise dashboard and reports
- Excel export with multiple sheets (period summary, daily summary, student details)
- Break tracking between periods

DATA STRUCTURE:
periods.json: [
    {
        "period_id": 1,
        "period_name": "Mathematics",
        "start_time": "09:00:00",
        "end_time": "10:00:00",
        "duration_minutes": 60,
        "subject": "Mathematics",
        "teacher": "Mr. Sharma",
        "is_break": false,
        "break_duration": 0
    },
    {
        "period_id": 2,
        "period_name": "BREAK",
        "start_time": "10:00:00",
        "end_time": "10:10:00",
        "duration_minutes": 10,
        "subject": "BREAK",
        "teacher": "",
        "is_break": true,
        "break_duration": 10
    }
]

attendance.json: {
    "2024-01-15": {
        "101": {
            "periods": {
                "1": {"entry": "09:00:05", "exit": "09:30:15", "duration": "00:30:10", "present": true},
                "2": {"entry": null, "exit": null, "duration": "00:00:00", "present": false},
                "3": {"entry": "10:10:15", "exit": "10:50:30", "duration": "00:40:15", "present": true}
            },
            "total_present": 2,
            "total_absent": 1,
            "total_duration": "01:10:25"
        }
    }
}

FEATURES:
1. Period CRUD interface
2. Real-time period indicator during attendance
3. Automatic period transition detection
4. Break tracking with movement monitoring
5. Grace period (5 minutes) for late arrivals
6. Early departure detection
7. Period-wise analytics
8. Daily summary report
9. Student movement timeline
10. Teacher-specific period assignments

USE ANTI-GRAVITY LOGGING:
- @antigravity_trace for all period operations
- @track_runtime_value for period transition calculations
- Log period changes, attendance marking per period
- Monitor period duration calculations
"""

# PERIOD-WISE ATTENDANCE CODE TO ADD TO YOUR app.py
import os
import json
import csv
import pandas as pd
from datetime import datetime, timedelta, time
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from logger_config import antigravity_trace, track_runtime_value

# ==================== PERIOD MANAGEMENT CONFIGURATION ====================
PERIODS_FILE = os.path.join(BASE_DIR, 'periods.json')
ATTENDANCE_PERIOD_FILE = os.path.join(BASE_DIR, 'attendance_period.json')
GRACE_PERIOD_MINUTES = 5  # 5 minutes grace period for late arrival
MIN_ATTENDANCE_PERCENTAGE = 60  # Minimum 60% attendance required per period

# ==================== PERIOD MANAGEMENT FUNCTIONS ====================
@antigravity_trace
def load_periods():
    """Load period configurations from JSON file"""
    if not os.path.exists(PERIODS_FILE):
        # Create default periods (example: school day)
        default_periods = [
            {
                "period_id": 1,
                "period_name": "Mathematics",
                "start_time": "09:00:00",
                "end_time": "10:00:00",
                "duration_minutes": 60,
                "subject": "Mathematics",
                "teacher": "Mr. Sharma",
                "is_break": False,
                "break_duration": 0,
                "is_active": True
            },
            {
                "period_id": 2,
                "period_name": "BREAK",
                "start_time": "10:00:00",
                "end_time": "10:10:00",
                "duration_minutes": 10,
                "subject": "BREAK",
                "teacher": "",
                "is_break": True,
                "break_duration": 10,
                "is_active": True
            },
            {
                "period_id": 3,
                "period_name": "Physics",
                "start_time": "10:10:00",
                "end_time": "11:10:00",
                "duration_minutes": 60,
                "subject": "Physics",
                "teacher": "Ms. Patel",
                "is_break": False,
                "break_duration": 0,
                "is_active": True
            },
            {
                "period_id": 4,
                "period_name": "Chemistry",
                "start_time": "11:10:00",
                "end_time": "12:10:00",
                "duration_minutes": 60,
                "subject": "Chemistry",
                "teacher": "Dr. Kumar",
                "is_break": False,
                "break_duration": 0,
                "is_active": True
            },
            {
                "period_id": 5,
                "period_name": "LUNCH BREAK",
                "start_time": "12:10:00",
                "end_time": "13:00:00",
                "duration_minutes": 50,
                "subject": "BREAK",
                "teacher": "",
                "is_break": True,
                "break_duration": 50,
                "is_active": True
            },
            {
                "period_id": 6,
                "period_name": "Computer Science",
                "start_time": "13:00:00",
                "end_time": "14:00:00",
                "duration_minutes": 60,
                "subject": "Computer Science",
                "teacher": "Mrs. Gupta",
                "is_break": False,
                "break_duration": 0,
                "is_active": True
            },
            {
                "period_id": 7,
                "period_name": "English",
                "start_time": "14:00:00",
                "end_time": "15:00:00",
                "duration_minutes": 60,
                "subject": "English",
                "teacher": "Ms. Roy",
                "is_break": False,
                "break_duration": 0,
                "is_active": True
            }
        ]
        save_periods(default_periods)
        return default_periods
    
    try:
        with open(PERIODS_FILE, 'r') as f:
            periods = json.load(f)
            # Sort periods by start time
            periods.sort(key=lambda x: datetime.strptime(x['start_time'], '%H:%M:%S'))
            return periods
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading periods: {e}")
        return []

@antigravity_trace
def save_periods(periods_data):
    """Save period configurations to JSON file"""
    try:
        with open(PERIODS_FILE, 'w') as f:
            json.dump(periods_data, f, indent=4)
    except IOError as e:
        print(f"Error saving periods: {e}")
        raise

@antigravity_trace
def get_current_period():
    """Get current period based on current time"""
    now = datetime.now().time()
    periods = load_periods()
    
    for period in periods:
        if not period.get('is_active', True):
            continue
            
        start_time = datetime.strptime(period['start_time'], '%H:%M:%S').time()
        end_time = datetime.strptime(period['end_time'], '%H:%M:%S').time()
        
        # Check if current time is within period (with grace period)
        grace_start = (datetime.combine(datetime.today(), start_time) - 
                      timedelta(minutes=GRACE_PERIOD_MINUTES)).time()
        grace_end = (datetime.combine(datetime.today(), end_time) + 
                     timedelta(minutes=GRACE_PERIOD_MINUTES)).time()
        
        if grace_start <= now <= grace_end:
            return period
    
    return None

@antigravity_trace
def get_period_by_id(period_id):
    """Get period by ID"""
    periods = load_periods()
    for period in periods:
        if period['period_id'] == period_id:
            return period
    return None

@antigravity_trace
def get_next_period():
    """Get next period after current time"""
    now = datetime.now().time()
    periods = load_periods()
    
    for period in periods:
        if not period.get('is_active', True):
            continue
            
        start_time = datetime.strptime(period['start_time'], '%H:%M:%S').time()
        if start_time > now:
            return period
    
    return None

@antigravity_trace
def calculate_period_duration(entry_time_str, exit_time_str):
    """Calculate duration between entry and exit times"""
    if not entry_time_str or not exit_time_str:
        return "00:00:00"
    
    try:
        entry_time = datetime.strptime(entry_time_str, '%H:%M:%S')
        exit_time = datetime.strptime(exit_time_str, '%H:%M:%S')
        
        if exit_time < entry_time:
            # Handle overnight scenario (not typical for school)
            exit_time = exit_time + timedelta(days=1)
        
        duration = exit_time - entry_time
        return str(duration)
    except ValueError as e:
        print(f"Error calculating duration: {e}")
        return "00:00:00"

@antigravity_trace
def is_within_period_window(period):
    """Check if current time is within attendance window for period"""
    now = datetime.now().time()
    start_time = datetime.strptime(period['start_time'], '%H:%M:%S').time()
    end_time = datetime.strptime(period['end_time'], '%H:%M:%S').time()
    
    grace_start = (datetime.combine(datetime.today(), start_time) - 
                  timedelta(minutes=GRACE_PERIOD_MINUTES)).time()
    grace_end = (datetime.combine(datetime.today(), end_time) + 
                 timedelta(minutes=GRACE_PERIOD_MINUTES)).time()
    
    return grace_start <= now <= grace_end

# ==================== PERIOD-WISE ATTENDANCE FUNCTIONS ====================
@antigravity_trace
def load_period_attendance():
    """Load period-wise attendance data"""
    if not os.path.exists(ATTENDANCE_PERIOD_FILE):
        return {}
    
    try:
        with open(ATTENDANCE_PERIOD_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading period attendance: {e}")
        return {}

@antigravity_trace
def save_period_attendance(attendance_data):
    """Save period-wise attendance data"""
    try:
        with open(ATTENDANCE_PERIOD_FILE, 'w') as f:
            json.dump(attendance_data, f, indent=4)
    except IOError as e:
        print(f"Error saving period attendance: {e}")
        raise

@antigravity_trace
def mark_period_attendance(roll_no, period_id, entry_time=None, exit_time=None):
    """Mark attendance for a specific period"""
    today_str = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")
    
    attendance_data = load_period_attendance()
    
    # Initialize day data if not exists
    if today_str not in attendance_data:
        attendance_data[today_str] = {}
    
    # Initialize student data if not exists
    if roll_no not in attendance_data[today_str]:
        attendance_data[today_str][roll_no] = {
            "periods": {},
            "total_present": 0,
            "total_absent": 0,
            "total_duration": "00:00:00"
        }
    
    student_data = attendance_data[today_str][roll_no]
    
    # Initialize period data if not exists
    if str(period_id) not in student_data["periods"]:
        student_data["periods"][str(period_id)] = {
            "entry": None,
            "exit": None,
            "duration": "00:00:00",
            "present": False,
            "attendance_percentage": 0
        }
    
    period_data = student_data["periods"][str(period_id)]
    
    # Update entry or exit time
    if entry_time:
        period_data["entry"] = entry_time
        period_data["present"] = True
        
        # Update total present count
        if not period_data.get("counted", False):
            student_data["total_present"] += 1
            period_data["counted"] = True
    
    if exit_time:
        period_data["exit"] = exit_time
        
        # Calculate duration if both entry and exit exist
        if period_data["entry"]:
            duration = calculate_period_duration(period_data["entry"], exit_time)
            period_data["duration"] = duration
            
            # Update total duration
            total_duration = datetime.strptime(student_data["total_duration"], '%H:%M:%S')
            period_duration = datetime.strptime(duration, '%H:%M:%S')
            new_total = (datetime.combine(datetime.today(), total_duration.time()) + 
                        timedelta(hours=period_duration.hour, 
                                minutes=period_duration.minute, 
                                seconds=period_duration.second))
            student_data["total_duration"] = new_total.strftime('%H:%M:%S')
            
            # Calculate attendance percentage for period
            period = get_period_by_id(period_id)
            if period and not period.get('is_break', False):
                period_duration_seconds = period['duration_minutes'] * 60
                attended_seconds = (period_duration.hour * 3600 + 
                                  period_duration.minute * 60 + 
                                  period_duration.second)
                percentage = (attended_seconds / period_duration_seconds) * 100
                period_data["attendance_percentage"] = round(percentage, 2)
    
    # Save updated attendance
    save_period_attendance(attendance_data)
    
    return period_data

@antigravity_trace
def get_student_period_attendance(roll_no, date_str=None):
    """Get period attendance for a specific student on a specific date"""
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    attendance_data = load_period_attendance()
    
    if date_str in attendance_data and roll_no in attendance_data[date_str]:
        return attendance_data[date_str][roll_no]
    
    return None

@antigravity_trace
def get_daily_period_summary(date_str=None):
    """Get daily summary of period attendance"""
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    attendance_data = load_period_attendance()
    students = load_students()
    periods = load_periods()
    
    if date_str not in attendance_data:
        return {
            "date": date_str,
            "total_students": len(students),
            "period_summary": {},
            "overall_attendance": 0
        }
    
    day_data = attendance_data[date_str]
    
    # Initialize period summary
    period_summary = {}
    for period in periods:
        if not period.get('is_active', True) or period.get('is_break', False):
            continue
        
        period_id = period['period_id']
        period_summary[period_id] = {
            "period_name": period['period_name'],
            "subject": period['subject'],
            "teacher": period['teacher'],
            "total_students": len(students),
            "present": 0,
            "absent": len(students),
            "attendance_percentage": 0,
            "average_duration": "00:00:00"
        }
    
    # Calculate period-wise statistics
    total_present_all = 0
    total_periods_all = 0
    
    for roll_no, student_data in day_data.items():
        for period_id_str, period_data in student_data.get("periods", {}).items():
            period_id = int(period_id_str)
            
            if period_id in period_summary and period_data.get("present", False):
                period_summary[period_id]["present"] += 1
                period_summary[period_id]["absent"] -= 1
                
                # Track for overall calculation
                total_present_all += 1
    
    # Calculate percentages
    for period_id, summary in period_summary.items():
        if summary["total_students"] > 0:
            summary["attendance_percentage"] = round(
                (summary["present"] / summary["total_students"]) * 100, 2
            )
        
        total_periods_all += 1
    
    # Calculate overall attendance
    total_possible = len(students) * total_periods_all
    overall_attendance = 0
    if total_possible > 0:
        overall_attendance = round((total_present_all / total_possible) * 100, 2)
    
    return {
        "date": date_str,
        "total_students": len(students),
        "period_summary": period_summary,
        "overall_attendance": overall_attendance,
        "total_present_all": total_present_all,
        "total_periods": total_periods_all
    }

# ==================== PERIOD MANAGEMENT ROUTES ====================
@app.route("/periods")
@login_required
@role_required('admin', 'teacher')
@antigravity_trace
def manage_periods():
    """Manage periods page"""
    periods = load_periods()
    return render_template('periods.html', periods=periods)

@app.route("/periods/add", methods=["GET", "POST"])
@login_required
@role_required('admin')
@antigravity_trace
def add_period():
    """Add new period"""
    if request.method == 'POST':
        period_name = request.form.get('period_name', '').strip()
        start_time = request.form.get('start_time', '').strip()
        end_time = request.form.get('end_time', '').strip()
        subject = request.form.get('subject', '').strip()
        teacher = request.form.get('teacher', '').strip()
        is_break = request.form.get('is_break') == 'on'
        
        # Validate times
        try:
            start_dt = datetime.strptime(start_time, '%H:%M')
            end_dt = datetime.strptime(end_time, '%H:%M')
            
            if end_dt <= start_dt:
                flash("End time must be after start time", "error")
                return redirect(url_for('add_period'))
            
            duration = (end_dt - start_dt).seconds // 60
            
        except ValueError:
            flash("Invalid time format. Use HH:MM", "error")
            return redirect(url_for('add_period'))
        
        periods = load_periods()
        
        # Check for overlapping periods
        for period in periods:
            if not period.get('is_active', True):
                continue
            
            existing_start = datetime.strptime(period['start_time'], '%H:%M:%S')
            existing_end = datetime.strptime(period['end_time'], '%H:%M:%S')
            
            if (start_dt < existing_end and end_dt > existing_start):
                flash(f"Period overlaps with {period['period_name']}", "error")
                return redirect(url_for('add_period'))
        
        # Create new period
        new_period_id = max([p['period_id'] for p in periods], default=0) + 1
        
        new_period = {
            "period_id": new_period_id,
            "period_name": period_name,
            "start_time": start_time + ":00",
            "end_time": end_time + ":00",
            "duration_minutes": duration,
            "subject": subject,
            "teacher": teacher,
            "is_break": is_break,
            "break_duration": duration if is_break else 0,
            "is_active": True
        }
        
        periods.append(new_period)
        save_periods(periods)
        
        flash(f"Period '{period_name}' added successfully", "success")
        return redirect(url_for('manage_periods'))
    
    return render_template('add_period.html')

@app.route("/periods/edit/<int:period_id>", methods=["GET", "POST"])
@login_required
@role_required('admin')
@antigravity_trace
def edit_period(period_id):
    """Edit existing period"""
    periods = load_periods()
    period = get_period_by_id(period_id)
    
    if not period:
        flash("Period not found", "error")
        return redirect(url_for('manage_periods'))
    
    if request.method == 'POST':
        period_name = request.form.get('period_name', '').strip()
        start_time = request.form.get('start_time', '').strip()
        end_time = request.form.get('end_time', '').strip()
        subject = request.form.get('subject', '').strip()
        teacher = request.form.get('teacher', '').strip()
        is_break = request.form.get('is_break') == 'on'
        is_active = request.form.get('is_active') == 'on'
        
        # Validate times
        try:
            start_dt = datetime.strptime(start_time, '%H:%M')
            end_dt = datetime.strptime(end_time, '%H:%M')
            
            if end_dt <= start_dt:
                flash("End time must be after start time", "error")
                return redirect(url_for('edit_period', period_id=period_id))
            
            duration = (end_dt - start_dt).seconds // 60
            
        except ValueError:
            flash("Invalid time format. Use HH:MM", "error")
            return redirect(url_for('edit_period', period_id=period_id))
        
        # Check for overlapping periods (excluding current period)
        for p in periods:
            if p['period_id'] == period_id or not p.get('is_active', True):
                continue
            
            existing_start = datetime.strptime(p['start_time'], '%H:%M:%S')
            existing_end = datetime.strptime(p['end_time'], '%H:%M:%S')
            
            if (start_dt < existing_end and end_dt > existing_start):
                flash(f"Period overlaps with {p['period_name']}", "error")
                return redirect(url_for('edit_period', period_id=period_id))
        
        # Update period
        for i, p in enumerate(periods):
            if p['period_id'] == period_id:
                periods[i] = {
                    "period_id": period_id,
                    "period_name": period_name,
                    "start_time": start_time + ":00",
                    "end_time": end_time + ":00",
                    "duration_minutes": duration,
                    "subject": subject,
                    "teacher": teacher,
                    "is_break": is_break,
                    "break_duration": duration if is_break else 0,
                    "is_active": is_active
                }
                break
        
        save_periods(periods)
        flash(f"Period '{period_name}' updated successfully", "success")
        return redirect(url_for('manage_periods'))
    
    return render_template('edit_period.html', period=period)

@app.route("/periods/delete/<int:period_id>")
@login_required
@role_required('admin')
@antigravity_trace
def delete_period(period_id):
    """Delete period (soft delete - mark as inactive)"""
    periods = load_periods()
    
    for i, period in enumerate(periods):
        if period['period_id'] == period_id:
            periods[i]['is_active'] = False
            save_periods(periods)
            flash(f"Period '{period['period_name']}' deactivated", "success")
            break
    
    return redirect(url_for('manage_periods'))

@app.route("/periods/activate/<int:period_id>")
@login_required
@role_required('admin')
@antigravity_trace
def activate_period(period_id):
    """Activate period"""
    periods = load_periods()
    
    for i, period in enumerate(periods):
        if period['period_id'] == period_id:
            periods[i]['is_active'] = True
            save_periods(periods)
            flash(f"Period '{period['period_name']}' activated", "success")
            break
    
    return redirect(url_for('manage_periods'))

# ==================== ENHANCED ATTENDANCE ROUTES ====================
@app.route("/attendance/period")
@login_required
@antigravity_trace
def attendance_period():
    """Period-wise attendance page"""
    current_period = get_current_period()
    next_period = get_next_period()
    periods = load_periods()
    
    return render_template('attendance_period.html', 
                         current_period=current_period,
                         next_period=next_period,
                         periods=periods)

def generate_period_attendance_frames():
    """Generate video feed with period-aware attendance tracking"""
    # Load Model
    if not os.path.exists(MODEL_FILE):
        yield from error_frame("Model not found! Train first.")
        return
    
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(MODEL_FILE)
    
    students = load_students()
    student_ids = {int(k): v for k, v in students.items() if k.isdigit()}
    
    camera = cv2.VideoCapture(0)
    
    # Trackers for period transitions
    period_trackers = {}  # {roll_no: {current_period_id, last_seen_time, state}}
    current_period = get_current_period()
    last_period_check = datetime.now()
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        # Check if period has changed (every 10 seconds)
        now = datetime.now()
        if (now - last_period_check).seconds >= 10:
            new_period = get_current_period()
            if new_period and current_period and new_period['period_id'] != current_period['period_id']:
                # Period changed - reset trackers
                period_trackers = {}
                flash_message = f"Period changed: {current_period['period_name']} → {new_period['period_name']}"
                print(flash_message)
                current_period = new_period
            
            last_period_check = now
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # Display current period info
        if current_period:
            period_info = f"{current_period['period_name']} ({current_period['start_time'][:5]} - {current_period['end_time'][:5]})"
            cv2.putText(frame, period_info, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            if current_period.get('is_break', False):
                cv2.putText(frame, "BREAK TIME", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw line for entry/exit tracking
        LINE_X = frame.shape[1] // 2
        cv2.line(frame, (LINE_X, 0), (LINE_X, frame.shape[0]), (0, 255, 255), 2)
        cv2.putText(frame, "EXIT <--- | ---> ENTRY", (10, frame.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        
        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            roi_gray = preprocess_face(roi_gray)
            
            try:
                id_, confidence = recognizer.predict(roi_gray)
                
                display_name = "Unknown"
                display_color = (0, 0, 255)
                
                if confidence < 70 and id_ in student_ids:
                    name = student_ids[id_].get("name", "Unknown")
                    display_name = f"{name}"
                    display_color = (0, 255, 0)
                    
                    roll_no = str(id_)
                    cx = x + w // 2
                    
                    # Period-aware attendance tracking
                    if current_period and not current_period.get('is_break', False):
                        if roll_no not in period_trackers:
                            period_trackers[roll_no] = {
                                'current_period_id': current_period['period_id'],
                                'last_x': cx,
                                'last_seen': now,
                                'state': 'outside'  # outside, entering, inside, exiting
                            }
                        
                        tracker = period_trackers[roll_no]
                        
                        # Update tracker
                        old_x = tracker['last_x']
                        tracker['last_x'] = cx
                        tracker['last_seen'] = now
                        
                        # Determine movement direction
                        if old_x < LINE_X and cx >= LINE_X:
                            # Entry into classroom
                            tracker['state'] = 'entering'
                            entry_time = now.strftime("%H:%M:%S")
                            
                            # Mark attendance for current period
                            mark_period_attendance(roll_no, current_period['period_id'], 
                                                  entry_time=entry_time)
                            
                            cv2.putText(frame, "ENTERED", (x, y-10), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            
                        elif old_x > LINE_X and cx <= LINE_X:
                            # Exit from classroom
                            tracker['state'] = 'exiting'
                            exit_time = now.strftime("%H:%M:%S")
                            
                            # Mark exit for current period
                            mark_period_attendance(roll_no, current_period['period_id'], 
                                                  exit_time=exit_time)
                            
                            cv2.putText(frame, "EXITED", (x, y-10), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                cv2.putText(frame, display_name, (x, y+h+20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, display_color, 2)
                
            except Exception as e:
                print(f"Recognition error: {e}")
            
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # Cleanup old trackers (5 minutes inactive)
        inactive_rolls = []
        for roll_no, tracker in period_trackers.items():
            if (now - tracker['last_seen']).seconds > 300:  # 5 minutes
                inactive_rolls.append(roll_no)
        
        for roll_no in inactive_rolls:
            del period_trackers[roll_no]
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    camera.release()

@app.route("/video_feed_period")
def video_feed_period():
    """Video feed for period-wise attendance"""
    return Response(generate_period_attendance_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# ==================== PERIOD-WISE REPORTS ====================
@app.route("/reports/period")
@login_required
@role_required('admin', 'teacher')
@antigravity_trace
def period_reports():
    """Period-wise reports page"""
    date_str = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    summary = get_daily_period_summary(date_str)
    
    return render_template('period_reports.html', summary=summary, selected_date=date_str)

@app.route("/reports/period/student/<roll_no>")
@login_required
@role_required('admin', 'teacher')
@antigravity_trace
def student_period_report(roll_no):
    """Student period-wise report"""
    date_str = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    student_data = get_student_period_attendance(roll_no, date_str)
    students = load_students()
    periods = load_periods()
    
    student_name = students.get(roll_no, {}).get('name', 'Unknown')
    
    # Prepare period details
    period_details = []
    for period in periods:
        if period.get('is_active', True):
            period_id = period['period_id']
            period_data = student_data.get('periods', {}).get(str(period_id), {}) if student_data else {}
            
            period_details.append({
                'period_id': period_id,
                'period_name': period['period_name'],
                'start_time': period['start_time'],
                'end_time': period['end_time'],
                'subject': period['subject'],
                'teacher': period['teacher'],
                'is_break': period.get('is_break', False),
                'entry': period_data.get('entry', '-'),
                'exit': period_data.get('exit', '-'),
                'duration': period_data.get('duration', '00:00:00'),
                'present': period_data.get('present', False),
                'attendance_percentage': period_data.get('attendance_percentage', 0)
            })
    
    return render_template('student_period_report.html',
                         roll_no=roll_no,
                         student_name=student_name,
                         date=date_str,
                         period_details=period_details,
                         student_data=student_data)

@app.route("/export/period")
@login_required
@role_required('admin', 'teacher')
@antigravity_trace
def export_period_attendance():
    """Export period-wise attendance to Excel"""
    date_str = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    
    # Load data
    attendance_data = load_period_attendance()
    students = load_students()
    periods = load_periods()
    
    # Filter active, non-break periods
    active_periods = [p for p in periods if p.get('is_active', True) and not p.get('is_break', False)]
    
    # Create Excel writer
    output_file = f'period_attendance_{date_str}.xlsx'
    output_path = os.path.join(BASE_DIR, output_file)
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Sheet 1: Daily Summary
        summary_data = []
        day_data = attendance_data.get(date_str, {})
        
        for roll_no, student_info in students.items():
            student_attendance = day_data.get(roll_no, {}) if day_data else {}
            
            total_present = student_attendance.get('total_present', 0)
            total_duration = student_attendance.get('total_duration', '00:00:00')
            
            summary_data.append({
                'Roll Number': roll_no,
                'Student Name': student_info.get('name', ''),
                'Total Periods': len(active_periods),
                'Present Periods': total_present,
                'Absent Periods': len(active_periods) - total_present,
                'Attendance %': round((total_present / len(active_periods)) * 100, 2) if active_periods else 0,
                'Total Duration': total_duration
            })
        
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Daily Summary', index=False)
        
        # Sheet 2: Period-wise Details
        period_details_data = []
        
        for period in active_periods:
            period_id = period['period_id']
            
            for roll_no, student_info in students.items():
                student_attendance = day_data.get(roll_no, {}) if day_data else {}
                period_data = student_attendance.get('periods', {}).get(str(period_id), {})
                
                period_details_data.append({
                    'Period ID': period_id,
                    'Period Name': period['period_name'],
                    'Time': f"{period['start_time'][:5]} - {period['end_time'][:5]}",
                    'Subject': period['subject'],
                    'Teacher': period['teacher'],
                    'Roll Number': roll_no,
                    'Student Name': student_info.get('name', ''),
                    'Entry Time': period_data.get('entry', 'ABSENT'),
                    'Exit Time': period_data.get('exit', 'ABSENT'),
                    'Duration': period_data.get('duration', '00:00:00'),
                    'Present': 'YES' if period_data.get('present', False) else 'NO',
                    'Attendance %': period_data.get('attendance_percentage', 0)
                })
        
        df_period_details = pd.DataFrame(period_details_data)
        df_period_details.to_excel(writer, sheet_name='Period Details', index=False)
        
        # Sheet 3: Period-wise Summary
        period_summary_data = []
        for period in active_periods:
            period_id = period['period_id']
            
            present_count = 0
            total_duration = timedelta()
            
            for roll_no, student_attendance in day_data.items():
                period_data = student_attendance.get('periods', {}).get(str(period_id), {})
                if period_data.get('present', False):
                    present_count += 1
                    if period_data.get('duration'):
                        try:
                            h, m, s = map(int, period_data['duration'].split(':'))
                            total_duration += timedelta(hours=h, minutes=m, seconds=s)
                        except:
                            pass
            
            avg_duration = total_duration / present_count if present_count > 0 else timedelta()
            
            period_summary_data.append({
                'Period ID': period_id,
                'Period Name': period['period_name'],
                'Subject': period['subject'],
                'Teacher': period['teacher'],
                'Total Students': len(students),
                'Present Students': present_count,
                'Absent Students': len(students) - present_count,
                'Attendance %': round((present_count / len(students)) * 100, 2),
                'Average Duration': str(avg_duration)[:7] if present_count > 0 else '00:00:00'
            })
        
        df_period_summary = pd.DataFrame(period_summary_data)
        df_period_summary.to_excel(writer, sheet_name='Period Summary', index=False)
        
        # Sheet 4: Student Timeline
        timeline_data = []
        for period in periods:  # Include breaks
            if not period.get('is_active', True):
                continue
            
            period_id = period['period_id']
            is_break = period.get('is_break', False)
            
            for roll_no, student_info in students.items():
                student_attendance = day_data.get(roll_no, {}) if day_data else {}
                period_data = student_attendance.get('periods', {}).get(str(period_id), {})
                
                status = 'BREAK' if is_break else 'ABSENT'
                if period_data.get('present', False):
                    status = 'PRESENT' if not is_break else 'BREAK_PRESENT'
                
                timeline_data.append({
                    'Time Slot': f"{period['start_time'][:5]} - {period['end_time'][:5]}",
                    'Period': period['period_name'],
                    'Type': 'BREAK' if is_break else 'CLASS',
                    'Roll Number': roll_no,
                    'Student Name': student_info.get('name', ''),
                    'Status': status,
                    'Entry': period_data.get('entry', '-'),
                    'Exit': period_data.get('exit', '-'),
                    'Duration': period_data.get('duration', '00:00:00')
                })
        
        df_timeline = pd.DataFrame(timeline_data)
        df_timeline.to_excel(writer, sheet_name='Student Timeline', index=False)
    
    return send_file(output_path, as_attachment=True)

# ==================== UPDATE EXISTING ROUTES ====================
@app.route("/dashboard")
@login_required
@antigravity_trace
def dashboard():
    """Main dashboard with period info"""
    # Load statistics
    students = load_students()
    attendance = load_attendance()
    current_period = get_current_period()
    daily_summary = get_daily_period_summary()
    
    # Calculate stats
    today = datetime.now().strftime("%Y-%m-%d")
    present_today = 0
    
    for roll_no, data in attendance.items():
        if 'entry' in data:
            present_today += 1
    
    stats = {
        'total_students': len(students),
        'present_today': present_today,
        'absent_today': len(students) - present_today,
        'attendance_rate': (present_today / len(students) * 100) if students else 0,
        'current_period': current_period,
        'daily_attendance_percentage': daily_summary.get('overall_attendance', 0)
    }
    
    return render_template('dashboard.html', stats=stats, user_role=session.get('user_role'))

# Update the home route to show period info if logged in
@app.route("/")
@antigravity_trace
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template("home.html")

# ==================== HELPER FUNCTIONS ====================
def error_frame(message):
    """Generate error frame"""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(frame, message, (50, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    ret, buffer = cv2.imencode('.jpg', frame)
    frame = buffer.tobytes()
    yield (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Add these imports if not already present
import numpy as np
```

## **TEMPLATE PROMPTS**

```
CREATE THE FOLLOWING TEMPLATES FOR PERIOD-WISE ATTENDANCE:

1. templates/periods.html - List all periods with CRUD operations
2. templates/add_period.html - Form to add new period
3. templates/edit_period.html - Form to edit period
4. templates/attendance_period.html - Attendance page with period info
5. templates/period_reports.html - Daily period-wise reports
6. templates/student_period_report.html - Individual student period report
7. templates/dashboard.html - Update to show period info

EACH TEMPLATE SHOULD INCLUDE:
- Responsive design with Bootstrap 5
- Current period display (if applicable)
- Period timeline visualization
- Real-time updates (AJAX for period changes)
- Export buttons for reports
- Clear status indicators (present/absent/break)
- Teacher and subject information
- Time-based color coding (current/upcoming/completed periods)
```

## **IMMEDIATE IMPLEMENTATION STEPS:**

1. **Add the period management code** to your `app.py`
2. **Create the template files** with the structure above
3. **Update your existing attendance logic** to use period tracking
4. **Test with sample periods** (9:00-10:00 Math, 10:00-10:10 Break, etc.)
5. **Verify period transitions** work correctly
6. **Test Excel export** with period data

This system will now track attendance per period, handle breaks, and provide detailed period-wise reports - exactly what you need for whole-day attendance tracking!