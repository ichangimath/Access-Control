#!/usr/bin/env python3

import json
import os
import psutil
import subprocess
import threading
import time

# Global variable and lock to track whether the task is running
task_running = False
task_running_lock = threading.Lock()

def close_process(process_name):
	for proc in psutil.process_iter(['pid', 'name']):
		if proc.info['name'] == process_name:
			proc.kill()
			print(f"Process {process_name} terminated.")
			
def check_process(process_name_check):
	for proc in psutil.process_iter(['pid', 'name']):
		if proc.info['name'] == process_name_check:
			return True
	return False

def read_access_setting():
	try:
		with open(os.environ.get("accessControl_settings_path"), "r") as file:
			settings = json.load(file)
			return settings
	except FileNotFoundError:
		print("Settings file not found.")
	except Exception as e:
		print("Error reading settings:", e)
	return {}

def periodic_task():
	global task_running
	with task_running_lock:
		if not task_running:
			task_running = True
		else:
			return
		
	try:
		settings = read_access_setting()
		access = settings.get("access")
		process_close_A = settings.get("process_close_A")
		process_close_B = settings.get("process_close_B")
		process_open = settings.get("process_open")
		process_open_path = settings.get("process_open_path")
		
		print(process_close_A)
		print(process_close_B)
		print(process_open)
		print(process_open_path)
		
		if access == "closed":
			close_process(process_close_A)
			close_process(process_close_B)
		if check_process(process_open):
			print(process_open + " is open")
		if not check_process(process_open):
			print("trying to open " + process_open)
			subprocess.Popen(process_open_path)
	except Exception as e:
		print("Error in periodic task:", e)
	finally:
		with task_running_lock:
			task_running = False
			threading.Timer(2, periodic_task).start()
			
def start_periodic_task():
	threading.Timer(2, periodic_task).start()
	
if __name__ == "__main__":
	start_periodic_task()  # Start the periodic task
	