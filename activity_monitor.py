from datetime import datetime
import os
import time
import threading
import psutil # For process information

# Attempt to import platform-specific modules for active window
try:
    import pygetwindow as gw
except ImportError:
    gw = None
    print("Warning: pygetwindow not installed. Active window logging may be limited.")

LOG_DIR = "logs"
ACTIVITY_LOG_FILE_PREFIX = "activity_logs_"

class ActivityMonitor:
    def __init__(self, interval_seconds=5):
        self.interval = interval_seconds
        self.running = False
        self.log_file = None
        self._ensure_log_directory()
        self._open_log_file()
        self.last_active_window = None

    def _ensure_log_directory(self):
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)

    def _get_log_filename(self):
        return os.path.join(LOG_DIR, f"{ACTIVITY_LOG_FILE_PREFIX}{datetime.now().strftime('%Y-%m-%d')}.txt")

    def _open_log_file(self):
        if self.log_file and not self.log_file.closed:
            self.log_file.close()
        self.log_file = open(self._get_log_filename(), "a", encoding="utf-8")

    def _get_active_window_title(self):
        if gw:
            try:
                active_window = gw.getActiveWindow()
                if active_window:
                    return active_window.title
            except Exception as e:
                return f"Error getting window title: {e}"
        return "Unknown Application (pygetwindow not available or error)"

    def _log_activity(self):
        current_window = self._get_active_window_title()
        if current_window and current_window != self.last_active_window:
            log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Active Window: {current_window}\n"
            self._write_to_log(log_entry)
            self.last_active_window = current_window

    def _write_to_log(self, entry):
        # Re-open log file if date changes
        current_log_filename = self._get_log_filename()
        if self.log_file.name != current_log_filename:
            self._open_log_file()
        self.log_file.write(entry)
        self.log_file.flush()

    def start_monitoring(self):
        if not self.running:
            self.running = True
            print(f"Activity monitor started with interval {self.interval} seconds...")
            while self.running:
                self._log_activity()
                time.sleep(self.interval)
            print("Activity monitor stopped.")

    def stop_monitoring(self):
        if self.running:
            self.running = False
            if self.log_file and not self.log_file.closed:
                self.log_file.close()
            print("Activity monitor stopped.")

# Example usage (for testing activity_monitor.py directly)
if __name__ == "__main__":
    monitor = ActivityMonitor(interval_seconds=3)
    monitor_thread = threading.Thread(target=monitor.start_monitoring)
    monitor_thread.start()
    print("Activity monitor thread started. Monitoring for 30 seconds.")
    time.sleep(30)
    monitor.stop_monitoring()
    monitor_thread.join() # Wait for the thread to finish