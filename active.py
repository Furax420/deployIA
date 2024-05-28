import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import subprocess
import requests
import time
import getpass

class InstallationPathWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Deployment Tool")
        self.geometry("600x400")

        self.previous_installation_path = ""
        self.create_widgets()
        self.check_saved_path()

    def create_widgets(self):
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.label = ctk.CTkLabel(self.main_frame, text="Welcome to the Deployment Tool!")
        self.label.pack(pady=10)

        user_documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        if os.path.exists(os.path.join(user_documents_path, ".path_ia$.txt")):
            with open(os.path.join(user_documents_path, ".path_ia$.txt"), "r") as file:
                self.previous_installation_path = file.read().strip()

        if self.previous_installation_path:
            self.path_label_text = f"Previous Installation Path: {self.previous_installation_path}"
        else:
            self.path_label_text = "Previous Installation Path not found"

        self.path_label = ctk.CTkLabel(self.main_frame, text=self.path_label_text)
        self.path_label.pack(pady=5)

        self.change_button = ctk.CTkButton(self.main_frame, text="Change Path", command=self.change_path)
        self.change_button.pack(pady=10)

        self.continue_button = ctk.CTkButton(self.main_frame, text="Continue", command=self.save_and_continue)
        self.continue_button.pack(pady=10)

    def check_saved_path(self):
        user_documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        if os.path.exists(os.path.join(user_documents_path, ".path_ia$.txt")):
            with open(os.path.join(user_documents_path, ".path_ia$.txt"), "r") as file:
                self.previous_installation_path = file.read().strip()

    def change_path(self):
        folder_selected = filedialog.askdirectory(initialdir=os.path.expanduser("~/Documents"))
        if folder_selected:
            self.previous_installation_path = folder_selected
            self.path_label.configure(text=f"Previous Installation Path: {self.previous_installation_path}")

    def save_and_continue(self):
        if not self.previous_installation_path:
            messagebox.showerror("Error", "Please select a valid installation path.")
            return

        user_documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        with open(os.path.join(user_documents_path, ".path_ia$.txt"), "w") as file:
            file.write(self.previous_installation_path)

        # Close the current window and open the main application window
        self.destroy()
        MainApplicationWindow(self.previous_installation_path)


class MainApplicationWindow(ctk.CTk):
    def __init__(self, installation_path):
        super().__init__()

        self.title("Deployment Tool")
        self.geometry("600x400")

        self.installation_path = installation_path
        self.server_running = False

        self.create_widgets()

    def create_widgets(self):
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.path_label = ctk.CTkLabel(self.main_frame, text=f"Installation Path: {self.installation_path}")
        self.path_label.pack(pady=5)

        self.server_button = ctk.CTkButton(self.main_frame, text="Start Server", command=self.toggle_server)
        self.server_button.pack(pady=20)

def toggle_server(self):
    if not self.server_running:
        # Start the server
        try:
            backend_path = os.path.join(self.installation_path, "backend")
            activate_script = os.path.join(backend_path, "env", "Scripts", "activate")
            dev_script = os.path.join(backend_path, "dev.sh")

            # Activate the virtual environment and start the development server
            subprocess.Popen(["bash", "-c", f"source {activate_script} && ./dev.sh"], cwd=backend_path)

            # Check if the server is running
            time.sleep(2)  # Wait for the server to start
            response = requests.get("http://localhost:80")
            if response.status_code == 200:
                self.server_button.configure(text="Stop Server")
                messagebox.showinfo("Server Status", "Server is running")
                self.server_running = True
            else:
                messagebox.showerror("Error", "Failed to start the server.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while starting the server: {e}")
    else:
        # Stop the server
        try:
            subprocess.Popen(["bash", "-c", "kill -2 $(lsof -t -i:80)"])
            self.server_button.configure(text="Start Server")
            self.server_running = False
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while stopping the server: {e}")


if __name__ == "__main__":
    app = InstallationPathWindow()
    app.mainloop()

