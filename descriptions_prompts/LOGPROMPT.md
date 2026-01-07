phase 1 : "Act as a Senior Python Developer. Create a centralized logging utility module for a Flask and OpenCV project. The utility should use Python's logging module and RotatingFileHandler. It must support different log levels (INFO for general flow, DEBUG for OpenCV frame data, and ERROR for Haar Cascade failures). Ensure the logs include timestamps, the filename, and the line number. Also, include a helper function to export these logs into a JSON format so I can read them later using my app's existing JSON logic."

phase 2 : "Write a Python decorator function called trace_performance for my OpenCV tasks. This decorator should calculate the execution time of any function it wraps. When a function finishes, it should log the function name, the time taken in milliseconds, and any specific 'runtime values' passed to it (like image resolution or number of objects detected). Apply this decorator logic to a sample OpenCV Haar Cascade function to demonstrate how it tracks performance without interrupting the video stream."

phase 3 : "Create a 'weightless' (asynchronous) logging mechanism for my app.py using QueueHandler or a separate thread. Since I am using OpenCV, I don't want the file-writing process to slow down my frame rate (FPS). Like the 'antigravity' module, make this logging system feel invisible. It should capture 'runtime values' like CPU usage and memory consumption during the Haar Cascade process and write them to a log file in the background without blocking the main Flask thread."

phase 4 : "I have a Flask app with an HTML/CSS frontend. Provide a Python route in app.py that reads the last 20 lines of my app.log file and returns them as a JSON object. Then, provide a simple JavaScript snippet to fetch this data every 5 seconds and display it in a 'Developer Console' <div> on my HTML page so I can track the program execution in real-time."

How to use these in your project:
Create a logger_config.py: Use the output from the Architect prompt.

Import it in app.py: Use from logger_config import trace_performance.

Wrap your OpenCV logic: ```python @trace_performance def process_frame(frame): # Haar cascade logic here