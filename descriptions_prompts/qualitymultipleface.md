I'll enhance your face recognition system with improved accuracy, better camera instructions, real-time logging, and multiple face detection. Here are the comprehensive improvements:

## 1. Enhanced Face Recognition with Multiple Improvements

### Updated `generate_attendance_frames()` function with enhanced features:

```python
# --- Enhanced Face Recognition with Multiple Improvements ---
from collections import deque
import math

# Enhanced preprocessing with more techniques
@antigravity_trace
def enhanced_preprocess_face(face_img):
    """
    Enhanced face preprocessing with multiple techniques:
    1. Adaptive histogram equalization (CLAHE)
    2. Gaussian blur for noise reduction
    3. Sharpening filter
    4. Gamma correction
    5. Edge enhancement
    """
    try:
        # Resize to standard size
        face_img = cv2.resize(face_img, (200, 200))
        
        # Step 1: CLAHE for contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        face_img = clahe.apply(face_img)
        
        # Step 2: Gaussian blur (light) for noise reduction
        face_img = cv2.GaussianBlur(face_img, (3, 3), 0)
        
        # Step 3: Sharpening filter
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        face_img = cv2.filter2D(face_img, -1, kernel)
        
        # Step 4: Gamma correction
        gamma = 1.2
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        face_img = cv2.LUT(face_img, table)
        
    except Exception as e:
        print(f"Error in enhanced preprocessing: {e}")
        # Fallback to simple resize
        face_img = cv2.resize(face_img, (200, 200))
        
    return face_img

@antigravity_trace
def calculate_face_quality(face_img):
    """
    Calculate face image quality metrics:
    Returns: blur_score, brightness_score, contrast_score, overall_quality
    """
    try:
        # Blur detection using Laplacian variance
        blur_score = cv2.Laplacian(face_img, cv2.CV_64F).var()
        
        # Brightness (0-255, optimal around 128)
        brightness_score = np.mean(face_img)
        
        # Contrast (standard deviation)
        contrast_score = np.std(face_img)
        
        # Overall quality score (0-100)
        blur_quality = min(blur_score / 100, 1) * 40  # Max 40 points
        brightness_quality = 30 - abs(brightness_score - 128) / 128 * 30  # Max 30 points
        contrast_quality = min(contrast_score / 50, 1) * 30  # Max 30 points
        
        overall_quality = blur_quality + brightness_quality + contrast_quality
        
        return {
            'blur_score': blur_score,
            'brightness_score': brightness_score,
            'contrast_score': contrast_score,
            'overall_quality': overall_quality
        }
    except Exception as e:
        print(f"Error calculating face quality: {e}")
        return {'blur_score': 0, 'brightness_score': 0, 'contrast_score': 0, 'overall_quality': 0}

class EnhancedFaceTracker:
    """Enhanced face tracking with Kalman filter for smooth movement"""
    def __init__(self):
        self.trackers = {}
        self.verification_buffers = {}
        self.recognition_history = {}
        self.kalman_filters = {}
        
    def update_kalman(self, roll_no, x, y):
        """Update Kalman filter for smooth tracking"""
        if roll_no not in self.kalman_filters:
            # Initialize Kalman filter
            kf = cv2.KalmanFilter(4, 2)
            kf.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
            kf.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
            kf.processNoiseCov = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32) * 0.03
            self.kalman_filters[roll_no] = kf
        
        kf = self.kalman_filters[roll_no]
        kf.correct(np.array([[np.float32(x)], [np.float32(y)]]))
        predicted = kf.predict()
        return int(predicted[0][0]), int(predicted[1][0])
    
    def update_recognition_history(self, roll_no, confidence, is_match):
        """Maintain recognition history for reliability"""
        if roll_no not in self.recognition_history:
            self.recognition_history[roll_no] = deque(maxlen=10)
        
        self.recognition_history[roll_no].append({
            'confidence': confidence,
            'is_match': is_match,
            'timestamp': time.time()
        })
        
    def get_recognition_reliability(self, roll_no):
        """Calculate recognition reliability score"""
        if roll_no not in self.recognition_history or len(self.recognition_history[roll_no]) < 3:
            return 0.5  # Default medium reliability
        
        history = list(self.recognition_history[roll_no])
        recent_matches = sum(1 for h in history[-5:] if h['is_match'])
        avg_confidence = np.mean([h['confidence'] for h in history[-5:]])
        
        reliability = (recent_matches / 5) * 0.6 + (1 - avg_confidence / 100) * 0.4
        return min(max(reliability, 0), 1)

# Global enhanced tracker
enhanced_tracker = EnhancedFaceTracker()

# Global attendance log
attendance_log = deque(maxlen=100)  # Store last 100 entries

def log_attendance_event(event_type, roll_no, name, confidence, quality_metrics=None):
    """Log attendance events with timestamps"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    event_data = {
        'timestamp': timestamp,
        'event_type': event_type,
        'roll_no': roll_no,
        'name': name,
        'confidence': confidence,
        'quality_metrics': quality_metrics
    }
    
    attendance_log.append(event_data)
    print(f"[LOG] {timestamp} - {event_type}: {name} ({roll_no}) - Confidence: {confidence}")

def generate_enhanced_attendance_frames():
    """Enhanced attendance tracking with multiple improvements"""
    # Load Model
    if not os.path.exists(MODEL_FILE):
        yield from error_frame("Model not found! Train first.")
        return
    
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(MODEL_FILE)
    
    # Load Student Names
    students = load_students()
    
    camera = cv2.VideoCapture(0)
    
    # Set camera properties for better quality
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    camera.set(cv2.CAP_PROP_FPS, 30)
    camera.set(cv2.CAP_PROP_BRIGHTNESS, 128)
    camera.set(cv2.CAP_PROP_CONTRAST, 128)
    
    # Virtual Line X-Coordinate
    LINE_X = 640
    
    # Face detection parameters
    scale_factor = 1.1
    min_neighbors = 5
    min_size = (100, 100)
    
    # Confidence threshold
    MATCH_THRESHOLD = 65  # Adjusted for enhanced preprocessing
    
    # Camera quality monitoring
    frame_count = 0
    last_quality_check = 0
    camera_quality_issues = []
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        frame_count += 1
        frame_time = time.time()
        
        # Resize frame for better performance
        frame_resized = cv2.resize(frame, (960, 540))
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
        
        # Periodically check camera quality
        if frame_time - last_quality_check > 5:  # Every 5 seconds
            camera_quality_issues = check_camera_quality(frame_resized)
            last_quality_check = frame_time
        
        # Enhanced face detection with multiple scales
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=scale_factor,
            minNeighbors=min_neighbors,
            minSize=min_size,
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        # Draw Line and instructions
        cv2.line(frame_resized, (LINE_X, 0), (LINE_X, 540), (0, 255, 255), 3)
        cv2.putText(frame_resized, "EXIT <--- | ---> ENTRY", (10, 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Display camera quality issues
        y_offset = 40
        for issue in camera_quality_issues:
            cv2.putText(frame_resized, issue, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            y_offset += 20
        
        # Track multiple faces
        current_time = time.time()
        
        for (x, y, w, h) in faces:
            # Scale coordinates back to original frame size
            x_orig, y_orig, w_orig, h_orig = x, y, w, h
            
            # Draw face rectangle
            cv2.rectangle(frame_resized, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Extract face ROI
            roi_gray = gray[y:y+h, x:x+w]
            
            # Calculate face quality metrics
            quality_metrics = calculate_face_quality(roi_gray)
            
            # Preprocess face
            roi_processed = enhanced_preprocess_face(roi_gray)
            
            # Predict with confidence
            try:
                id_, confidence = recognizer.predict(roi_processed)
                
                # Get face center for tracking
                cx = x + w // 2
                cy = y + h // 2
                
                display_name = "Unknown"
                display_color = (0, 0, 255)  # Red for unknown
                roll_no = "unknown"
                name = "Unknown Person"
                
                # Quality feedback text
                quality_text = ""
                if quality_metrics['blur_score'] < 50:
                    quality_text = "Too blurry!"
                elif quality_metrics['brightness_score'] < 50:
                    quality_text = "Too dark!"
                elif quality_metrics['brightness_score'] > 200:
                    quality_text = "Too bright!"
                elif quality_metrics['overall_quality'] < 50:
                    quality_text = "Poor quality!"
                
                if quality_text:
                    cv2.putText(frame_resized, quality_text, (x, y-30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                
                # Check if recognized
                if confidence < MATCH_THRESHOLD:
                    roll_no = str(id_)
                    name = students.get(roll_no, {}).get("name", "Unknown")
                    
                    # Update verification buffer
                    if roll_no not in enhanced_tracker.verification_buffers:
                        enhanced_tracker.verification_buffers[roll_no] = deque(maxlen=5)
                    enhanced_tracker.verification_buffers[roll_no].append(True)
                    
                    # Check verification (at least 3/5 frames match)
                    buffer = list(enhanced_tracker.verification_buffers[roll_no])
                    verified = len(buffer) >= 3 and sum(buffer[-3:]) >= 2
                    
                    if verified:
                        display_name = f"{name} ({roll_no})"
                        display_color = (0, 255, 0)  # Green for recognized
                        
                        # Update recognition history
                        enhanced_tracker.update_recognition_history(roll_no, confidence, True)
                        
                        # Get reliability score
                        reliability = enhanced_tracker.get_recognition_reliability(roll_no)
                        
                        # Add reliability indicator
                        if reliability > 0.8:
                            reliability_text = "High"
                            reliability_color = (0, 255, 0)
                        elif reliability > 0.5:
                            reliability_text = "Medium"
                            reliability_color = (0, 255, 255)
                        else:
                            reliability_text = "Low"
                            reliability_color = (0, 165, 255)
                        
                        cv2.putText(frame_resized, f"Reliability: {reliability_text}", 
                                   (x, y+h+40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, reliability_color, 1)
                        
                        # Tracking logic
                        if roll_no not in enhanced_tracker.trackers:
                            enhanced_tracker.trackers[roll_no] = {
                                'last_x': cx,
                                'last_y': cy,
                                'last_seen': current_time,
                                'state': 'outside',
                                'entry_time': None,
                                'exit_time': None
                            }
                        
                        tracker = enhanced_tracker.trackers[roll_no]
                        old_x = tracker['last_x']
                        
                        # Update with Kalman filter for smooth tracking
                        smoothed_x, smoothed_y = enhanced_tracker.update_kalman(roll_no, cx, cy)
                        
                        tracker['last_x'] = smoothed_x
                        tracker['last_y'] = smoothed_y
                        tracker['last_seen'] = current_time
                        
                        # Crossing detection with hysteresis
                        if tracker['state'] == 'outside' and smoothed_x >= LINE_X - 30 and smoothed_x <= LINE_X + 30:
                            # Approaching line
                            tracker['state'] = 'approaching'
                        
                        elif tracker['state'] == 'approaching' and smoothed_x >= LINE_X:
                            # Entry detected
                            tracker['state'] = 'inside'
                            tracker['entry_time'] = current_time
                            
                            # Log entry
                            log_attendance_event('ENTRY', roll_no, name, confidence, quality_metrics)
                            cv2.putText(frame_resized, "ENTRY MARKED", (x, y-10), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            
                            # Mark period attendance if within period
                            current_period = get_current_period()
                            if current_period and not current_period.get('is_break', False):
                                entry_time_str = datetime.datetime.now().strftime("%H:%M:%S")
                                mark_period_attendance(roll_no, current_period['period_id'], 
                                                      entry_time=entry_time_str)
                        
                        elif tracker['state'] == 'inside' and smoothed_x <= LINE_X:
                            # Exit detected
                            tracker['state'] = 'outside'
                            tracker['exit_time'] = current_time
                            
                            # Log exit
                            log_attendance_event('EXIT', roll_no, name, confidence, quality_metrics)
                            cv2.putText(frame_resized, "EXIT MARKED", (x, y-10), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            
                            # Mark period exit if within period
                            current_period = get_current_period()
                            if current_period and not current_period.get('is_break', False):
                                exit_time_str = datetime.datetime.now().strftime("%H:%M:%S")
                                mark_period_attendance(roll_no, current_period['period_id'], 
                                                      exit_time=exit_time_str)
                    else:
                        display_name = "Verifying..."
                        display_color = (0, 255, 255)  # Yellow for verifying
                else:
                    # Unknown person detected
                    roll_no = "unknown"
                    name = "Unknown Person"
                    display_name = "Unknown"
                    display_color = (0, 0, 255)
                    
                    # Log unknown person detection
                    if frame_count % 10 == 0:  # Log every 10th frame to avoid spam
                        log_attendance_event('UNKNOWN_DETECTED', 'unknown', 'Unknown Person', 
                                           confidence, quality_metrics)
                
                # Display name and confidence
                confidence_text = f"Conf: {int(confidence)}"
                cv2.putText(frame_resized, display_name, (x, y+h+20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, display_color, 2)
                cv2.putText(frame_resized, confidence_text, (x, y+h+60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, display_color, 1)
                
                # Display quality metrics
                if quality_metrics['overall_quality'] < 60:
                    quality_warning = f"Quality: {int(quality_metrics['overall_quality'])}%"
                    cv2.putText(frame_resized, quality_warning, (x, y+h+80), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 1)
                
            except Exception as e:
                print(f"Recognition error: {e}")
                continue
        
        # Cleanup old trackers (2 minutes inactive)
        inactive_rolls = []
        for roll_no, tracker in enhanced_tracker.trackers.items():
            if current_time - tracker['last_seen'] > 120:  # 2 minutes
                inactive_rolls.append(roll_no)
        
        for roll_no in inactive_rolls:
            del enhanced_tracker.trackers[roll_no]
            if roll_no in enhanced_tracker.kalman_filters:
                del enhanced_tracker.kalman_filters[roll_no]
        
        # Display statistics
        stats_text = f"Faces: {len(faces)} | Known: {len([f for f in faces if display_name != 'Unknown'])}"
        cv2.putText(frame_resized, stats_text, (10, frame_resized.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Convert frame for streaming
        ret, buffer = cv2.imencode('.jpg', frame_resized)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    camera.release()

def check_camera_quality(frame):
    """Check camera quality and return issues"""
    issues = []
    
    # Convert to grayscale for analysis
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Check blur
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
    if blur_score < 50:
        issues.append("⚠ Camera blurry - adjust focus")
    
    # Check brightness
    brightness = np.mean(gray)
    if brightness < 50:
        issues.append("⚠ Too dark - improve lighting")
    elif brightness > 200:
        issues.append("⚠ Too bright - reduce lighting")
    
    # Check contrast
    contrast = np.std(gray)
    if contrast < 30:
        issues.append("⚠ Low contrast - adjust camera settings")
    
    return issues

# Updated video feed route
@app.route("/video_feed_attendance")
def video_feed_attendance():
    """Video feed for enhanced attendance tracking"""
    return Response(generate_enhanced_attendance_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')
```

## 2. Real-Time Log Display Page

Create a new template `attendance_log.html`:

```html
<!-- templates/attendance_log.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Attendance Log - Attendance Management System</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }

        .log-container {
            max-width: 1400px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        @media (max-width: 1024px) {
            .log-container {
                grid-template-columns: 1fr;
            }
        }

        .video-section {
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .log-section {
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
        }

        .section-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }

        .section-header h2 {
            margin: 0;
            font-size: 1.5em;
            font-weight: 300;
        }

        .video-container {
            padding: 20px;
            text-align: center;
        }

        #videoFeed {
            max-width: 100%;
            border-radius: 10px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }

        .log-container-inner {
            flex: 1;
            display: flex;
            flex-direction: column;
        }

        .log-controls {
            padding: 15px 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #eaeaea;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .btn {
            padding: 8px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 0.9em;
            transition: all 0.3s ease;
        }

        .btn:hover {
            background: #5a67d8;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        .btn-danger {
            background: #dc3545;
        }

        .btn-danger:hover {
            background: #c82333;
        }

        .btn-success {
            background: #28a745;
        }

        .btn-success:hover {
            background: #218838;
        }

        .stats-container {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            padding: 15px 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #eaeaea;
        }

        .stat-box {
            background: white;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 3px 10px rgba(0,0,0,0.05);
        }

        .stat-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }

        .stat-label {
            font-size: 0.8em;
            color: #666;
            margin-top: 5px;
        }

        .log-table-container {
            flex: 1;
            overflow-y: auto;
            max-height: 600px;
        }

        .log-table {
            width: 100%;
            border-collapse: collapse;
        }

        .log-table th {
            position: sticky;
            top: 0;
            background: #667eea;
            color: white;
            padding: 12px 15px;
            text-align: left;
            font-weight: 500;
            z-index: 10;
        }

        .log-table td {
            padding: 12px 15px;
            border-bottom: 1px solid #eaeaea;
        }

        .log-table tr:hover {
            background: #f8f9fa;
        }

        .event-entry {
            border-left: 4px solid #28a745;
        }

        .event-exit {
            border-left: 4px solid #dc3545;
        }

        .event-unknown {
            border-left: 4px solid #ffc107;
        }

        .event-error {
            border-left: 4px solid #6c757d;
        }

        .confidence-high {
            color: #28a745;
            font-weight: bold;
        }

        .confidence-medium {
            color: #ffc107;
            font-weight: bold;
        }

        .confidence-low {
            color: #dc3545;
            font-weight: bold;
        }

        .status-badge {
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
        }

        .status-present {
            background: #d4edda;
            color: #155724;
        }

        .status-absent {
            background: #f8d7da;
            color: #721c24;
        }

        .status-unknown {
            background: #fff3cd;
            color: #856404;
        }

        .refresh-indicator {
            padding: 10px 20px;
            text-align: center;
            background: #f8f9fa;
            color: #666;
            font-size: 0.9em;
            border-top: 1px solid #eaeaea;
        }

        .auto-refresh {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .switch {
            position: relative;
            display: inline-block;
            width: 50px;
            height: 24px;
        }

        .switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }

        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 34px;
        }

        .slider:before {
            position: absolute;
            content: "";
            height: 16px;
            width: 16px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }

        input:checked + .slider {
            background-color: #667eea;
        }

        input:checked + .slider:before {
            transform: translateX(26px);
        }

        .no-data {
            text-align: center;
            padding: 40px;
            color: #666;
            font-style: italic;
        }

        .instructions {
            background: #e8f4fd;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin: 15px 20px;
            border-radius: 5px;
            font-size: 0.9em;
        }

        .instructions h4 {
            margin-top: 0;
            color: #1976D2;
        }

        .instructions ul {
            margin: 10px 0;
            padding-left: 20px;
        }

        .instructions li {
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <div class="log-container">
        <!-- Video Section -->
        <div class="video-section">
            <div class="section-header">
                <h2>📹 Live Camera Feed</h2>
            </div>
            <div class="video-container">
                <img id="videoFeed" src="{{ url_for('video_feed_attendance') }}" 
                     alt="Live Camera Feed" crossorigin="anonymous">
                
                <div class="instructions">
                    <h4>📋 Camera Instructions:</h4>
                    <ul>
                        <li>Ensure good lighting on faces</li>
                        <li>Maintain 1-2 feet distance from camera</li>
                        <li>Look straight at the camera</li>
                        <li>Move slowly across the yellow line</li>
                        <li>Green: Recognized student | Red: Unknown person</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- Log Section -->
        <div class="log-section">
            <div class="section-header">
                <h2>📝 Real-Time Attendance Log</h2>
            </div>
            
            <div class="log-container-inner">
                <div class="log-controls">
                    <div class="auto-refresh">
                        <span>Auto-refresh:</span>
                        <label class="switch">
                            <input type="checkbox" id="autoRefresh" checked>
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="control-buttons">
                        <button class="btn btn-danger" onclick="clearLog()">
                            <span>🗑️</span> Clear Log
                        </button>
                        <a href="{{ url_for('export_attendance_log') }}" class="btn btn-success">
                            <span>📥</span> Export Excel
                        </a>
                    </div>
                </div>

                <div class="stats-container">
                    <div class="stat-box">
                        <div class="stat-value" id="totalEntries">0</div>
                        <div class="stat-label">Total Entries</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value" id="studentsPresent">0</div>
                        <div class="stat-label">Students Present</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value" id="unknownDetected">0</div>
                        <div class="stat-label">Unknown Persons</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value" id="currentTime">--:--</div>
                        <div class="stat-label">Current Time</div>
                    </div>
                </div>

                <div class="log-table-container">
                    <table class="log-table" id="attendanceLogTable">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Event</th>
                                <th>Roll No</th>
                                <th>Name</th>
                                <th>Confidence</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody id="logTableBody">
                            <!-- Log entries will be inserted here -->
                        </tbody>
                    </table>
                    <div id="noDataMessage" class="no-data" style="display: none;">
                        No attendance data recorded yet.
                    </div>
                </div>

                <div class="refresh-indicator">
                    <span id="lastUpdate">Last updated: Just now</span>
                    <span id="refreshStatus" style="margin-left: 20px;"></span>
                </div>
            </div>
        </div>
    </div>

    <script>
        let autoRefreshEnabled = true;
        let refreshInterval;
        let lastLogCount = 0;

        // Update current time
        function updateCurrentTime() {
            const now = new Date();
            const timeString = now.toLocaleTimeString();
            document.getElementById('currentTime').textContent = timeString;
        }

        // Fetch log data
        async function fetchLogData() {
            try {
                const response = await fetch('/api/attendance/log');
                const data = await response.json();
                
                if (data.success) {
                    updateLogTable(data.log_entries);
                    updateStatistics(data.statistics);
                    
                    // Update last updated time
                    const now = new Date();
                    document.getElementById('lastUpdate').textContent = 
                        `Last updated: ${now.toLocaleTimeString()}`;
                        
                    // Show refresh status
                    if (data.log_entries.length > lastLogCount) {
                        document.getElementById('refreshStatus').textContent = 
                            `▲ ${data.log_entries.length - lastLogCount} new entries`;
                        document.getElementById('refreshStatus').style.color = '#28a745';
                    } else if (data.log_entries.length < lastLogCount) {
                        document.getElementById('refreshStatus').textContent = 
                            `▼ ${lastLogCount - data.log_entries.length} entries cleared`;
                        document.getElementById('refreshStatus').style.color = '#dc3545';
                    } else {
                        document.getElementById('refreshStatus').textContent = '';
                    }
                    
                    lastLogCount = data.log_entries.length;
                }
            } catch (error) {
                console.error('Error fetching log data:', error);
                document.getElementById('refreshStatus').textContent = 'Error fetching data';
                document.getElementById('refreshStatus').style.color = '#dc3545';
            }
        }

        // Update log table
        function updateLogTable(entries) {
            const tableBody = document.getElementById('logTableBody');
            const noDataMessage = document.getElementById('noDataMessage');
            
            if (entries.length === 0) {
                tableBody.innerHTML = '';
                noDataMessage.style.display = 'block';
                return;
            }
            
            noDataMessage.style.display = 'none';
            
            // Sort entries by timestamp (newest first)
            entries.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
            
            let tableHTML = '';
            
            entries.forEach(entry => {
                const eventClass = `event-${entry.event_type.toLowerCase().split('_')[0]}`;
                const confidenceClass = getConfidenceClass(entry.confidence);
                const statusBadge = getStatusBadge(entry.event_type);
                
                tableHTML += `
                    <tr class="${eventClass}">
                        <td>${entry.timestamp.split(' ')[1]}</td>
                        <td>
                            <span class="status-badge ${statusBadge.class}">
                                ${statusBadge.text}
                            </span>
                        </td>
                        <td><strong>${entry.roll_no}</strong></td>
                        <td>${entry.name}</td>
                        <td class="${confidenceClass}">${entry.confidence}%</td>
                        <td>
                            <span style="color: #666; font-size: 0.9em;">
                                ${entry.quality_issues || ''}
                            </span>
                        </td>
                    </tr>
                `;
            });
            
            tableBody.innerHTML = tableHTML;
        }

        // Update statistics
        function updateStatistics(stats) {
            document.getElementById('totalEntries').textContent = stats.total_entries;
            document.getElementById('studentsPresent').textContent = stats.students_present;
            document.getElementById('unknownDetected').textContent = stats.unknown_detected;
        }

        // Get confidence class
        function getConfidenceClass(confidence) {
            if (confidence >= 80) return 'confidence-high';
            if (confidence >= 60) return 'confidence-medium';
            return 'confidence-low';
        }

        // Get status badge
        function getStatusBadge(eventType) {
            switch(eventType) {
                case 'ENTRY':
                    return { class: 'status-present', text: 'ENTRY' };
                case 'EXIT':
                    return { class: 'status-absent', text: 'EXIT' };
                case 'UNKNOWN_DETECTED':
                    return { class: 'status-unknown', text: 'UNKNOWN' };
                default:
                    return { class: '', text: eventType };
            }
        }

        // Clear log
        async function clearLog() {
            if (confirm('Are you sure you want to clear the attendance log? This cannot be undone.')) {
                try {
                    const response = await fetch('/api/attendance/log/clear', { method: 'POST' });
                    const data = await response.json();
                    
                    if (data.success) {
                        alert('Log cleared successfully');
                        fetchLogData();
                    }
                } catch (error) {
                    alert('Error clearing log');
                    console.error(error);
                }
            }
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            // Update time every second
            updateCurrentTime();
            setInterval(updateCurrentTime, 1000);
            
            // Initial fetch
            fetchLogData();
            
            // Set up auto-refresh
            refreshInterval = setInterval(fetchLogData, 3000); // Update every 3 seconds
            
            // Auto-refresh toggle
            document.getElementById('autoRefresh').addEventListener('change', function(e) {
                autoRefreshEnabled = e.target.checked;
                
                if (autoRefreshEnabled) {
                    refreshInterval = setInterval(fetchLogData, 3000);
                    document.getElementById('refreshStatus').textContent = 'Auto-refresh enabled';
                    document.getElementById('refreshStatus').style.color = '#28a745';
                } else {
                    clearInterval(refreshInterval);
                    document.getElementById('refreshStatus').textContent = 'Auto-refresh disabled';
                    document.getElementById('refreshStatus').style.color = '#dc3545';
                }
            });
            
            // Manual refresh button (optional)
            document.addEventListener('keydown', function(e) {
                if (e.ctrlKey && e.key === 'r') {
                    e.preventDefault();
                    fetchLogData();
                }
            });
        });
    </script>
</body>
</html>
```

## 3. API Endpoints for Log Management

Add these API endpoints to your app.py:

```python
# ==================== ATTENDANCE LOG API ====================
@app.route("/api/attendance/log")
@login_required
@antigravity_trace
def get_attendance_log():
    """Get attendance log data"""
    try:
        # Convert deque to list
        log_entries = list(attendance_log)
        
        # Calculate statistics
        total_entries = len(log_entries)
        students_present = len([e for e in log_entries if e['event_type'] == 'ENTRY'])
        unknown_detected = len([e for e in log_entries if e['event_type'] == 'UNKNOWN_DETECTED'])
        
        # Prepare log entries for display
        formatted_entries = []
        for entry in log_entries[-50:]:  # Last 50 entries
            formatted_entry = {
                'timestamp': entry['timestamp'],
                'event_type': entry['event_type'],
                'roll_no': entry['roll_no'],
                'name': entry['name'],
                'confidence': int(entry['confidence']) if entry['confidence'] else 0,
                'quality_issues': get_quality_issues(entry.get('quality_metrics'))
            }
            formatted_entries.append(formatted_entry)
        
        return jsonify({
            'success': True,
            'log_entries': formatted_entries,
            'statistics': {
                'total_entries': total_entries,
                'students_present': students_present,
                'unknown_detected': unknown_detected
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route("/api/attendance/log/clear", methods=["POST"])
@login_required
@role_required('admin')
@antigravity_trace
def clear_attendance_log():
    """Clear attendance log"""
    global attendance_log
    attendance_log.clear()
    return jsonify({'success': True, 'message': 'Log cleared successfully'})

def get_quality_issues(quality_metrics):
    """Get quality issues from metrics"""
    if not quality_metrics:
        return ""
    
    issues = []
    if quality_metrics.get('blur_score', 100) < 50:
        issues.append("Blurry")
    if quality_metrics.get('brightness_score', 128) < 50:
        issues.append("Dark")
    if quality_metrics.get('brightness_score', 128) > 200:
        issues.append("Bright")
    if quality_metrics.get('overall_quality', 100) < 60:
        issues.append("Poor Quality")
    
    return ", ".join(issues) if issues else "Good"

# ==================== EXPORT ATTENDANCE LOG ====================
@app.route("/export/attendance-log")
@login_required
@role_required('admin', 'teacher')
@antigravity_trace
def export_attendance_log():
    """Export attendance log to Excel"""
    try:
        # Get log data
        log_entries = list(attendance_log)
        
        if not log_entries:
            flash("No attendance log data to export", "warning")
            return redirect(url_for('attendance_log_page'))
        
        # Create DataFrame
        df_data = []
        for entry in log_entries:
            df_data.append({
                'Timestamp': entry['timestamp'],
                'Event Type': entry['event_type'],
                'Roll Number': entry['roll_no'],
                'Name': entry['name'],
                'Confidence %': int(entry['confidence']) if entry['confidence'] else 0,
                'Blur Score': entry.get('quality_metrics', {}).get('blur_score', 0),
                'Brightness': entry.get('quality_metrics', {}).get('brightness_score', 0),
                'Contrast': entry.get('quality_metrics', {}).get('contrast_score', 0),
                'Overall Quality %': entry.get('quality_metrics', {}).get('overall_quality', 0),
                'Quality Issues': get_quality_issues(entry.get('quality_metrics'))
            })
        
        df = pd.DataFrame(df_data)
        
        # Create Excel file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'attendance_log_{timestamp}.xlsx'
        filepath = os.path.join(BASE_DIR, filename)
        
        # Create Excel writer with multiple sheets
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Sheet 1: All log entries
            df.to_excel(writer, sheet_name='All Log Entries', index=False)
            
            # Sheet 2: Summary by student
            if len(df) > 0:
                student_summary = df[df['Roll Number'] != 'unknown'].groupby(['Roll Number', 'Name']).agg({
                    'Event Type': lambda x: (x == 'ENTRY').sum()
                }).rename(columns={'Event Type': 'Entry Count'}).reset_index()
                student_summary.to_excel(writer, sheet_name='Student Summary', index=False)
            
            # Sheet 3: Unknown detections
            unknown_detections = df[df['Roll Number'] == 'unknown']
            unknown_detections.to_excel(writer, sheet_name='Unknown Persons', index=False)
            
            # Sheet 4: Quality issues
            quality_issues = df[df['Quality Issues'] != '']
            quality_issues.to_excel(writer, sheet_name='Quality Issues', index=False)
        
        # Send file
        return send_file(filepath, as_attachment=True)
        
    except Exception as e:
        flash(f"Error exporting log: {str(e)}", "error")
        return redirect(url_for('attendance_log_page'))

# ==================== ATTENDANCE LOG PAGE ====================
@app.route("/attendance/log")
@login_required
@role_required('admin', 'teacher')
@antigravity_trace
def attendance_log_page():
    """Attendance log page with live camera and log"""
    return render_template("attendance_log.html")
```

## 4. Enhanced Face Capture with Better Instructions

Update your `generate_capture_frames()` function:

```python
def generate_enhanced_capture_frames(roll_no):
    """Enhanced face capture with better instructions and quality feedback"""
    camera = cv2.VideoCapture(0)
    
    # Set camera properties
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    camera.set(cv2.CAP_PROP_FPS, 30)
    
    # Path to save images
    student_folder = os.path.join(DATASET_DIR, roll_no)
    if not os.path.exists(student_folder):
        os.makedirs(student_folder, exist_ok=True)
        
    count = 0
    max_images = 50
    capture_states = [
        {"start": 0, "end": 10, "instruction": "Look straight at camera", "angle": "front"},
        {"start": 10, "end": 20, "instruction": "Turn head LEFT slowly", "angle": "left"},
        {"start": 20, "end": 30, "instruction": "Turn head RIGHT slowly", "angle": "right"},
        {"start": 30, "end": 40, "instruction": "Tilt head UP slightly", "angle": "up"},
        {"start": 40, "end": 50, "instruction": "Tilt head DOWN slightly", "angle": "down"}
    ]
    
    # Quality tracking
    quality_stats = {
        'blurry_count': 0,
        'dark_count': 0,
        'bright_count': 0,
        'good_count': 0
    }
    
    while True:
        success, frame = camera.read()
        if not success:
            break
            
        # Resize for display
        frame_resized = cv2.resize(frame, (960, 540))
        gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # Get current instruction
        current_state = None
        for state in capture_states:
            if state["start"] <= count < state["end"]:
                current_state = state
                break
        
        instruction = current_state["instruction"] if current_state else "Completed!"
        
        # Display main instruction
        cv2.putText(frame_resized, f"Instruction: {instruction}", 
                   (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        # Display progress
        cv2.putText(frame_resized, f"Progress: {count}/{max_images}", 
                   (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Display quality feedback
        cv2.putText(frame_resized, f"Quality: Blurry({quality_stats['blurry_count']}) Dark({quality_stats['dark_count']}) Good({quality_stats['good_count']})", 
                   (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame_resized, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Save face if within limit
            if count < max_images:
                roi_gray = gray[y:y+h, x:x+w]
                
                # Check face quality
                quality = calculate_face_quality(roi_gray)
                
                # Quality feedback
                if quality['blur_score'] < 30:
                    cv2.putText(frame_resized, "Too Blurry! Hold still", 
                               (x, y-30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    quality_stats['blurry_count'] += 1
                    continue
                elif quality['brightness_score'] < 50:
                    cv2.putText(frame_resized, "Too Dark! Move to light", 
                               (x, y-30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    quality_stats['dark_count'] += 1
                    continue
                elif quality['brightness_score'] > 200:
                    cv2.putText(frame_resized, "Too Bright! Reduce light", 
                               (x, y-30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    quality_stats['bright_count'] += 1
                    continue
                elif w < 100 or h < 100:
                    cv2.putText(frame_resized, "Too Far! Move closer", 
                               (x, y-30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    continue
                
                # Good quality - capture image
                count += 1
                face_img = enhanced_preprocess_face(roi_gray)
                
                # Save with angle information
                angle = current_state["angle"] if current_state else "front"
                img_path = os.path.join(student_folder, f"{count}_{angle}.jpg")
                cv2.imwrite(img_path, face_img)
                
                quality_stats['good_count'] += 1
                
                cv2.putText(frame_resized, "✓ Good!", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Completion message
        if count >= max_images:
            cv2.putText(frame_resized, "🎉 CAPTURE COMPLETE! You can go back.", 
                       (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame_resized, f"Good images: {quality_stats['good_count']}/{max_images}", 
                       (50, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame_resized)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
               
    camera.release()

# Update the video feed route for capture
@app.route("/video_feed_capture/<roll_no>")
def video_feed_capture(roll_no):
    return Response(generate_enhanced_capture_frames(roll_no), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')
```

## 5. Enhanced Model Training

Update your training function:

```python
@app.route("/train")
@login_required
@role_required('admin')
def train_model():
    """Enhanced model training with validation"""
    dataset_path = DATASET_DIR
    
    if not os.path.exists(dataset_path):
         flash("Dataset directory not found!", "error")
         return redirect(url_for("home"))
         
    faces, ids = get_images_and_labels(dataset_path)
    
    if not faces or not ids:
        flash("No training data found. Add students and capture photos first.", "error")
        return redirect(url_for("home"))
    
    # Enhanced LBPH parameters
    recognizer = cv2.face.LBPHFaceRecognizer_create(
        radius=2,
        neighbors=16,
        grid_x=10,
        grid_y=10,
        threshold=80  # Lower threshold for better accuracy
    )
    
    # Train with validation split
    total_samples = len(faces)
    split_idx = int(total_samples * 0.8)  # 80% training, 20% validation
    
    # Shuffle data
    combined = list(zip(faces, ids))
    import random
    random.shuffle(combined)
    faces[:], ids[:] = zip(*combined)
    
    # Split
    train_faces = faces[:split_idx]
    train_ids = ids[:split_idx]
    val_faces = faces[split_idx:]
    val_ids = ids[split_idx:]
    
    # Train
    recognizer.train(train_faces, np.array(train_ids))
    recognizer.save(MODEL_FILE)
    
    # Validate
    correct = 0
    total_val = len(val_faces)
    
    for i in range(total_val):
        try:
            pred_id, confidence = recognizer.predict(val_faces[i])
            if pred_id == val_ids[i] and confidence < 70:
                correct += 1
        except:
            pass
    
    accuracy = (correct / total_val * 100) if total_val > 0 else 0
    
    flash(f"Training Complete! Accuracy: {accuracy:.2f}%", "success")
    flash(f"Trained on {len(train_faces)} images, Validated on {total_val} images", "info")
    
    return redirect(url_for("home"))
```

## 6. Update Navigation Menu

Add the log page to your navigation:

```python
# In your navigation template
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('attendance_log_page') }}">
        <i class="fas fa-clipboard-list"></i> Live Log
    </a>
</li>
```

## 7. Key Improvements Summary:

1. **Enhanced Face Recognition**:
   - Kalman filter for smooth tracking
   - Reliability scoring based on history
   - Multi-frame verification
   - Better preprocessing with CLAHE, sharpening, gamma correction

2. **Camera Quality Monitoring**:
   - Real-time blur detection
   - Brightness/contrast warnings
   - Face quality scoring
   - Visual feedback on camera issues

3. **Real-Time Logging**:
   - Live log display with auto-refresh
   - Color-coded entries (green for entry, red for exit, yellow for unknown)
   - Statistics dashboard
   - Excel export with multiple sheets

4. **Multiple Face Detection**:
   - Simultaneous tracking of multiple faces
   - Individual tracking per face
   - Separate verification buffers per student

5. **Better Instructions**:
   - Clear camera instructions
   - Quality feedback during capture
   - Progress tracking
   - Angle-specific capture guidance

6. **Improved Accuracy**:
   - Enhanced preprocessing
   - Confidence thresholds
   - Reliability scoring
   - Validation during training

These improvements will significantly enhance your system's accuracy, provide better user feedback, and give administrators comprehensive logging and monitoring capabilities.