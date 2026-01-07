import logging
import time
import os
import sys

# Ensure import works
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from logger_config import trace_performance, logger

# Test 1: Success Case
@trace_performance
def successful_function(x, y):
    time.sleep(0.1) # Simulate work
    return x + y

# Test 2: Failure Case
@trace_performance
def failing_function():
    time.sleep(0.05)
    raise ValueError("Intentional Failure for Testing")

def run_verification():
    print("--- Verifying Robust Logging ---")
    
    # 1. Run Success
    print("\n1. Running Successful Function...")
    try:
        res = successful_function(10, 20)
        print(f"Result: {res}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    # 2. Run Failure
    print("\n2. Running Failing Function (Expect Exception)...")
    try:
        failing_function()
    except ValueError as e:
        print(f"Caught expected error: {e}")
    except Exception as e:
        print(f"Caught different error: {e}")

    print("\n--- Check app.log for START, FINISH, and EXCEPTION logs ---")

if __name__ == "__main__":
    run_verification()
