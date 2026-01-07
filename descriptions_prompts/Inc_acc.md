Improve face recognition accuracy in the SMARTO ATTEND web app.

IMPORTANT CONSTRAINTS:
- Must continue using OpenCV LBPH (opencv-contrib-python)
- Do NOT use face_recognition or dlib
- Must work on Windows + Python 3.11
- Must integrate into existing Flask app

PROBLEMS TO FIX:
- Live webcam often shows "UNKNOWN" even when student exists
- Recognition fails when face is slightly turned
- Dataset photos do not match live feed well

REQUIRED IMPROVEMENTS (MANDATORY):

1. FACE DATASET QUALITY
- Capture at least 50 images per student (not 30)
- Capture images with:
  - Straight face
  - Slight left turn
  - Slight right turn
  - Slight up/down tilt
- Enforce minimum face size before saving image
- Convert all images to grayscale
- Resize all face images to fixed size (200x200)

2. FACE PREPROCESSING (VERY IMPORTANT)
- Apply histogram equalization (cv2.equalizeHist)
- Apply Gaussian blur lightly to reduce noise
- Crop only the face region using Haar Cascade
- Reject blurry or partial face captures

3. TRAINING IMPROVEMENTS
- Ensure labels strictly match roll numbers
- Shuffle training data before training
- Train LBPH with parameters:
  - radius = 1
  - neighbors = 8
  - grid_x = 8
  - grid_y = 8
- Save trained model only after successful training

4. RECOGNITION CONFIDENCE LOGIC
- Use confidence threshold logic:
  - If confidence < 60 → Recognized
  - If confidence ≥ 60 → Unknown
- Display confidence score on live camera feed

5. LIVE CAMERA DETECTION
- Detect face every frame
- Track face center across frames
- Use last known identity for 10 frames to prevent flicker
- Allow recognition even if face is rotated up to ±25 degrees

6. LIGHTING NORMALIZATION
- Apply adaptive histogram equalization (CLAHE)
- Auto-adjust brightness for dark frames

7. MULTI-FRAME CONFIRMATION (CRITICAL)
- A student must be recognized in at least 5 consecutive frames
- Only then mark entry or exit
- Prevent false recognition from 1 frame

8. ATTENDANCE ROBUSTNESS
- Do not mark attendance if face is partially visible
- Do not mark attendance if face size < threshold
- Lock identity once entry is marked

9. DEBUGGING SUPPORT
- Show bounding box
- Show roll number, name, confidence
- Log recognition failures

OUTPUT EXPECTATION:
- Live camera should recognize student even with slight head turns
- Accuracy must be visibly higher than current version
- Unknown detection must reduce significantly
- Attendance should trigger reliably when face crosses vertical line

Implement all above improvements without changing app structure.
Explain key changes briefly in comments.
