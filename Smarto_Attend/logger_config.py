import logging
import json
import os
import time
import functools
import queue
import atexit
from logging.handlers import RotatingFileHandler, QueueHandler, QueueListener

try:
    import psutil
except ImportError:
    psutil = None

# Constants for log file
LOG_FILE = 'app.log'
MAX_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5

# Global listener reference to prevent garbage collection
_listener = None

def setup_logger(name=__name__):
    """
    Sets up a centralized logger with asynchronous file writing (QueueHandler).
    """
    global _listener
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Capture everything

    # Check if handlers already exist to avoid duplicate logs
    if not logger.handlers:
        # Create the actual file handler (worker)
        file_handler = RotatingFileHandler(LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT)
        file_handler.setLevel(logging.DEBUG)
        
        # Format: timestamp - filename:lineno - level - message
        formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Create a queue for async logging
        log_queue = queue.Queue(-1) # Infinite queue

        # Create QueueHandler (this stays on the main thread and is fast)
        queue_handler = QueueHandler(log_queue)
        logger.addHandler(queue_handler)

        # Create QueueListener (this runs in a separate thread)
        # It listens to the queue and dispatches details to the file_handler
        _listener = QueueListener(log_queue, file_handler)
        _listener.start()

        # Ensure listener stops gracefully on exit
        atexit.register(_listener.stop)
        
        # Optional: Add console handler (can be direct or async, keeping direct for immediate feedback)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

def export_logs_to_json(json_path='logs_export.json'):
    """
    Reads the log file and exports it to a JSON format.
    """
    logs = []
    if not os.path.exists(LOG_FILE):
        return logs

    try:
        with open(LOG_FILE, 'r') as f:
            for line in f:
                # Basic parsing
                parts = line.split(' - ')
                if len(parts) >= 4:
                    log_entry = {
                        'timestamp': parts[0],
                        'location': parts[1],
                        'level': parts[2],
                        'message': ' - '.join(parts[3:]).strip()
                    }
                    logs.append(log_entry)
        
        with open(json_path, 'w') as json_file:
            json.dump(logs, json_file, indent=4)
        
        return True
    except Exception as e:
        print(f"Error exporting logs: {e}")
        return False

# Initialize a default logger
logger = setup_logger()

# ContextVar for tracking internal state without passing variables around
import contextvars
_trace_context = contextvars.ContextVar('trace_context', default={})

def track_runtime_value(key, value):
    """
    Antigravity Helper: Log internal state changes without cluttering logic.
    Updates the current trace context with the given key-value pair.
    """
    ctx = _trace_context.get().copy()
    ctx[key] = value
    _trace_context.set(ctx)

def antigravity_trace(func):
    """
    Antigravity Decorator:
    - Zero-friction tracing (Start/End).
    - Captures Arguments.
    - Captures Runtime Values (via track_runtime_value).
    - Measures Duration.
    - Non-blocking logging.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Reset context for this call
        token = _trace_context.set({})
        
        # 1. Format Payload (Arguments)
        filtered_args = []
        for arg in args:
            if hasattr(arg, 'shape') and hasattr(arg, 'dtype'): 
                filtered_args.append(f"Array(shape={arg.shape})")
            else:
                filtered_args.append(arg)
        
        filtered_kwargs = {k: (f"Array(shape={v.shape})" if hasattr(v, 'shape') else v) for k, v in kwargs.items()}
        input_payload = f"Args: {filtered_args}, Kwargs: {filtered_kwargs}"
        if len(input_payload) > 300: input_payload = input_payload[:297] + "..."

        # 2. Log START (IN)
        # Format: [Function_Name] [Status: IN/OUT] [Duration] [Payload]
        # Timestamp is added by formatter
        logger.info(f"[{func.__name__}] [Status: IN] [Duration: 0ms] [Payload: {input_payload}]")

        start_time = time.time()
        
        try:
            # Execute
            result = func(*args, **kwargs)
            
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            # Get Runtime Values
            runtime_values = _trace_context.get()
            
            # Combine Return + Runtime Values for OUT payload
            output_payload = f"RuntimeValues: {runtime_values}"
            
            # 3. Log FINISH (OUT)
            logger.info(
                f"[{func.__name__}] [Status: OUT] [Duration: {duration_ms:.2f}ms] [Payload: {output_payload}]"
            )
            return result
            
        except Exception as e:
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            logger.error(
                f"[{func.__name__}] [Status: ERROR] [Duration: {duration_ms:.2f}ms] [Payload: Exception: {str(e)}]", 
                exc_info=True
            )
            raise e
        finally:
            _trace_context.reset(token)
            
    return wrapper

# Alias for backward compatibility if needed, or replace usage
trace_performance = antigravity_trace
