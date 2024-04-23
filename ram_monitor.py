
import psutil
import os
import time
import threading

# First method - it requires Thread
# Monitor memory usage every 10 sec 
def monitor_memory(interval=10):
    process = psutil.Process(os.getpid())
    while True:
        # Get memory usage statistics for the current process
        memory_mb = process.memory_info().rss / (1024 * 1024)  # Convert bytes to megabytes
        
        # Print memory usage in megabytes
        print(f"RAM Used by Process (MB): {memory_mb:.2f} MB")
        
        # Wait for the specified interval (in seconds)
        time.sleep(interval)
# Start the memory monitoring thread
memory_thread = threading.Thread(target=monitor_memory)
memory_thread.daemon = True
memory_thread.start()

# Second method - put it under app = Flask(__name__) in app.py
# Monitor memory usage before each request
# @app.before_request
# def log_memory_usage():
#     process = psutil.Process(os.getpid())
#     memory_mb = process.memory_info().rss / 1024 / 1024
#     print(f"Memory usage before {request.path}: {memory_mb} MB")
