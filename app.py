import streamlit as st
import threading
import os
# import time
import datetime

# Import our custom modules
from keylogger import KeyLogger, LOG_DIR, KEY_LOG_FILE_PREFIX
from activity_monitor import ActivityMonitor, ACTIVITY_LOG_FILE_PREFIX

# Session state initialization
if 'keylogger_running' not in st.session_state:
    st.session_state.keylogger_running = False
if 'activity_monitor_running' not in st.session_state:
    st.session_state.activity_monitor_running = False
if 'keylogger_thread' not in st.session_state:
    st.session_state.keylogger_thread = None
if 'activity_monitor_thread' not in st.session_state:
    st.session_state.activity_monitor_thread = None
if 'keylogger_instance' not in st.session_state:
    st.session_state.keylogger_instance = None
if 'activity_monitor_instance' not in st.session_state:
    st.session_state.activity_monitor_instance = None

st.set_page_config(layout="wide")
st.title("Simple Keylogger / Activity Logger (Educational Use Only)")

st.warning("⚠️ **Disclaimer:** This tool is for educational purposes only. Unauthorized use of keyloggers is illegal and unethical. Use responsibly and with explicit consent.")

# --- Keylogger Control ---
st.header("Keylogger Control")

def start_keylogger():
    if not st.session_state.keylogger_running:
        st.session_state.keylogger_instance = KeyLogger()
        st.session_state.keylogger_thread = threading.Thread(target=st.session_state.keylogger_instance.start_logging, daemon=True)
        st.session_state.keylogger_thread.start()
        st.session_state.keylogger_running = True
        st.success("Keylogger started.")
    else:
        st.info("Keylogger is already running.")

def stop_keylogger():
    if st.session_state.keylogger_running and st.session_state.keylogger_instance:
        st.session_state.keylogger_instance.stop_logging()
        if st.session_state.keylogger_thread and st.session_state.keylogger_thread.is_alive():
            # Give it a moment to stop
            st.session_state.keylogger_thread.join(timeout=2)
        st.session_state.keylogger_running = False
        st.success("Keylogger stopped.")
    else:
        st.info("Keylogger is not running.")

col1_kl, col2_kl = st.columns(2)
with col1_kl:
    if st.button("Start Keylogger", disabled=st.session_state.keylogger_running):
        start_keylogger()
with col2_kl:
    if st.button("Stop Keylogger", disabled=not st.session_state.keylogger_running):
        stop_keylogger()

st.write(f"Keylogger Status: {'Running' if st.session_state.keylogger_running else 'Stopped'}")

# --- Activity Monitor Control ---
st.header("Activity Monitor Control")

activity_interval = st.slider("Activity Logging Interval (seconds)", min_value=1, max_value=60, value=5)

def start_activity_monitor():
    if not st.session_state.activity_monitor_running:
        st.session_state.activity_monitor_instance = ActivityMonitor(interval_seconds=activity_interval)
        st.session_state.activity_monitor_thread = threading.Thread(target=st.session_state.activity_monitor_instance.start_monitoring, daemon=True)
        st.session_state.activity_monitor_thread.start()
        st.session_state.activity_monitor_running = True
        st.success("Activity Monitor started.")
    else:
        st.info("Activity Monitor is already running.")

def stop_activity_monitor():
    if st.session_state.activity_monitor_running and st.session_state.activity_monitor_instance:
        st.session_state.activity_monitor_instance.stop_monitoring()
        if st.session_state.activity_monitor_thread and st.session_state.activity_monitor_thread.is_alive():
            st.session_state.activity_monitor_thread.join(timeout=2)
        st.session_state.activity_monitor_running = False
        st.success("Activity Monitor stopped.")
    else:
        st.info("Activity Monitor is not running.")

col1_am, col2_am = st.columns(2)
with col1_am:
    if st.button("Start Activity Monitor", key="start_am_btn", disabled=st.session_state.activity_monitor_running):
        start_activity_monitor()
with col2_am:
    if st.button("Stop Activity Monitor", key="stop_am_btn", disabled=not st.session_state.activity_monitor_running):
        stop_activity_monitor()

st.write(f"Activity Monitor Status: {'Running' if st.session_state.activity_monitor_running else 'Stopped'}")

# --- View Logs ---
st.header("View Logs")

log_type = st.radio("Select Log Type", ("Key Logs", "Activity Logs"))

def get_log_files(prefix):
    if not os.path.exists(LOG_DIR):
        return []
    files = [f for f in os.listdir(LOG_DIR) if f.startswith(prefix) and f.endswith(".txt")]
    files.sort(reverse=True) # Show most recent first
    return files

current_log_prefix = KEY_LOG_FILE_PREFIX if log_type == "Key Logs" else ACTIVITY_LOG_FILE_PREFIX
available_log_files = get_log_files(current_log_prefix)

if available_log_files:
    selected_log_file = st.selectbox(
        f"Select {log_type} File",
        available_log_files
    )
    full_log_path = os.path.join(LOG_DIR, selected_log_file)
    if os.path.exists(full_log_path):
        st.subheader(f"Content of {selected_log_file}")
        try:
            with open(full_log_path, "r", encoding="utf-8", errors="ignore") as f:
                log_content = f.read()
            st.code(log_content, language="text")
        except Exception as e:
            st.error(f"Error reading log file: {e}")
    else:
        st.write("Selected log file not found.")
else:
    st.write(f"No {log_type} found yet.")

st.markdown("---")
st.info("Remember to stop logging before closing the application or browser tab to ensure all data is saved.")