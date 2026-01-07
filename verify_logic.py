
import sys
import os
import cv2
import numpy as np
from unittest.mock import MagicMock, patch

# Ensure we can import app
sys.path.append(os.path.join(os.getcwd(), 'Smarto_Attend'))

try:
    import app
    print("Successfully imported app.py")
except Exception as e:
    print(f"Failed to import app: {e}")
    # Try direct import if running from inside folder
    sys.path.append(os.getcwd())
    try:
        import app
        print("Successfully imported app.py (attempt 2)")
    except Exception as e2:
        print(f"Failed to import app: {e2}")
        sys.exit(1)

def test_preprocess():
    print("Testing preprocess_face...")
    dummy_img = np.zeros((300, 300), dtype=np.uint8)
    processed = app.preprocess_face(dummy_img)
    if processed.shape == (200, 200):
        print("PASS: Preprocess resize correct (200x200)")
    else:
        print(f"FAIL: Preprocess shape {processed.shape}")
    print("PASS: Preprocess ran without error")

def test_capture_logic():
    print("Testing capture logic generator...")
    
    with patch('cv2.VideoCapture') as mock_cap:
        mock_cam = MagicMock()
        mock_cap.return_value = mock_cam
        
        # valid frame
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Add a white rectangle to simulate a face so detection works (maybe)
        # Haar cascade won't detect on black, so generate_capture_frames might just yield the frame with text
        cv2.rectangle(dummy_frame, (100,100), (300,300), (255,255,255), -1)
        
        mock_cam.read.return_value = (True, dummy_frame)
        
        # We also need to patch face_cascade because it might complain or return empty
        # But real opencv is installed, so it should run (and return no faces on black image)
        
        gen = app.generate_capture_frames("TEST_ROLL")
        try:
            first_frame_data = next(gen)
            if b'--frame' in first_frame_data:
                print("PASS: Generator yielded frame data")
            else:
                print("FAIL: Generator yield format wrong")
                
            # Run a few more to check logic stability
            for _ in range(5):
                next(gen)
            print("PASS: Generator stable for multiple frames")
            
        except StopIteration:
            print("FAIL: Generator empty")
        except Exception as e:
            print(f"FAIL: Generator crashed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_preprocess()
    test_capture_logic()
