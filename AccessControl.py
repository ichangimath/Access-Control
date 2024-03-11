import tkinter as tk
from tkinter import ttk
import pandas as pd
import time
import requests
import json
import random
import string

global_font = ("Helvetica Bold", 20)

class AccessControlApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Access Control")

        self.time_start_label = ttk.Label(self, text="Started at:",font=global_font)
        self.time_start_label.grid(row=0, column=0, padx=15, pady=5, sticky="w")
        
        self.time_start_display = ttk.Label(self, text="",font=global_font)
        self.time_start_display.grid(row=0, column=1, padx=15, pady=5, sticky="w")
        
        self.time_end_label = ttk.Label(self, text="Closed at:",font=global_font)
        self.time_end_label.grid(row=1, column=0, padx=15, pady=5, sticky="w") 
        
        self.time_end_display = ttk.Label(self, text="",font=global_font)
        self.time_end_display.grid(row=1, column=1, padx=15, pady=5, sticky="w")
        
        self.dialog = ttk.Label(self, text="",font=global_font, foreground="red")
        self.dialog.grid(row=2, column=0, columnspan=2, padx=10, pady=15, sticky="w")
        
        self.student_id_label = ttk.Label(self, text="Enter Student ID:")
        self.student_id_label.grid(row=3, column=0, padx=15, pady=5, sticky="w")

        self.student_id_entry = ttk.Entry(self)
        self.student_id_entry.grid(row=3, column=1, padx=15, pady=5, sticky="w")

        self.email_label = ttk.Label(self, text="Enter Email Address:")
        self.email_label.grid(row=4, column=0, padx=15, pady=5, sticky="w")

        self.email_entry = ttk.Entry(self)
        self.email_entry.grid(row=4, column=1, padx=15, pady=5, sticky="w")

        self.submit_button = ttk.Button(self, text="Start Session", command=self.start_counter_and_check_access)
        self.submit_button.grid(row=5, column=0, padx=15, pady=5, sticky="w")

        self.close_button = ttk.Button(self, text="Close Session", command=self.close_session)
        self.close_button.grid(row=5, column=1, padx=15, pady=5, sticky="w")
        
        self.settings = self.load_settings()


    def load_settings(self):
        try:
            with open("settings.json", "r") as file:
                self.settings = json.load(file)
                
                if self.settings["access"] == "open":
                    self.submit_button.config(state="disabled")
                    self.student_id_entry.insert(0, self.settings["currentUser"])
                    self.email_entry.insert(0, self.settings["currentEmail"])
                    self.time_start_display.config(text=self.settings["timeStart"])
                    
        except FileNotFoundError:
            self.settings = None

    def fetch_approved_users(self):
        google_sheet_url = 'https://docs.google.com/spreadsheets/d/1CClXc2DX9pJggFvHXZccxhfUy3ETJkHIi2V1sjyqx-I/export?format=csv'
        df = pd.read_csv(google_sheet_url)
        approved_users = df[df.iloc[:, [10, 13, 14]].notnull().all(axis=1)]
        return approved_users

    def is_user_authorized(self):
        approved_users = self.fetch_approved_users()
        if self.student_id_entry.get() !="" :
            user_id = float(self.student_id_entry.get())
            associated_emails = approved_users.loc[approved_users['SIS User ID'] == user_id, 'SIS Login ID'].values
            email = self.email_entry.get()

            if email.split('@')[0] in associated_emails:
                return True
            else:
                self.dialog.config(text="INVALID CREDENTIALS")
                return False
        else:
            self.dialog.config(text="INVALID CREDENTIALS")
            return False

    def start_counter_and_check_access(self):
        if self.is_user_authorized():
            with open("settings.json", "r") as file:
                self.settings = json.load(file)
            student_id = self.student_id_entry.get()
            email = self.email_entry.get()
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            current_time = time.strftime("%H:%M")
            self.time_start_display.config(text=current_time)
            data = [[self.settings["UUID"], timestamp, self.settings["machine"], student_id, email]]
            self.send_data_to_google_script(data)
            self.submit_button.config(state="disabled")
            with open("settings.json", "w") as file:
                self.settings["access"] = "open"
                self.settings["currentUser"] = student_id
                self.settings["currentEmail"] = email
                self.settings["timeStart"] = current_time
                json.dump(self.settings, file)

    def close_session(self):
        if self.is_user_authorized():
#           self.stop_counter()
            with open("settings.json", "r") as file:
                self.settings = json.load(file)
            student_id = self.student_id_entry.get()
            email = self.email_entry.get()
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            current_time = time.strftime("%H:%M")
            self.time_end_display.config(text=current_time)
            data = [[self.settings["UUID"], timestamp]]
            self.send_data_to_google_script(data)
#           self.reset_counter()
            self.submit_button.config(state="normal")
            newUUID = ''.join(random.choices(string.ascii_letters + string.digits, k=8)) #rest UUID
            with open("settings.json", "w") as file:
                self.settings["UUID"] = newUUID
                self.settings["access"] = "closed"
                self.settings["currentUser"] = ""
                self.settings["currentEmail"] = ""
                self.settings["timeStart"] = ""
                json.dump(self.settings, file)
            print("Session closed.")
            self.student_id_entry.delete(0, tk.END)
            self.email_entry.delete(0, tk.END)
        else:
            print("User is not authorized. Data not sent.")

    def send_data_to_google_script(self, data):
        url = "https://script.google.com/macros/s/AKfycbyvQJ_2KKZp8Rnxo9-bAebwq6XbfXFlQZWRUonJBj3lXElcYsM29lN154Xa0ypSbRye4g/exec"
        response = requests.post(url, data=json.dumps(data))
        print(response.text)

def main():
    app = AccessControlApp()
    app.mainloop()

if __name__ == "__main__":
    main()
    