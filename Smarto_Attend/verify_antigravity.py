import logging
import time
import os
import sys

# Ensure import works
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from logger_config import antigravity_trace, track_runtime_value, logger

# Test Function with Internal State
@antigravity_trace
def processing_logic(image_size):
    time.sleep(0.05) # Simulate processing
    
    # Internal state change we want to log without returning it
    internal_confidence = 0.95
    track_runtime_value("confidence", internal_confidence)
    
    track_runtime_value("steps_completed", 5)
    
    return "Processed"

def run_verification():
    print("--- Verifying Antigravity Tracing ---")
    
    # Run Function
    print("\nRunning processing_logic...")
    res = processing_logic((1920, 1080))
    print(f"Result: {res}")

    print("\n--- Check app.log for 'RuntimeValues' in Payload ---")

if __name__ == "__main__":
    run_verification()
