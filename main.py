import os
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import customtkinter as ctk

class DeploymentTool(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Deployment Tool")
        self.geometry("800x600")

        self.install_path = tk.StringVar(value=os.path.expanduser("~/Documents"))
        self.selected_image_path = None
        self.image_list = []  # List to hold the CTkImage objects

        self.create_widgets()

    def create_widgets(self):
        self.select_frame = ctk.CTkFrame(self)
        self.select_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.label = ctk.CTkLabel(self.select_frame, text="Choose installation directory:")
        self.label.pack(pady=5)

        self.entry = ctk.CTkEntry(self.select_frame, textvariable=self.install_path, width=400)
        self.entry.pack(pady=5)

        self.browse_button = ctk.CTkButton(self.select_frame, text="Browse", command=self.choose_directory)
        self.browse_button.pack(pady=5)

        self.next_button = ctk.CTkButton(self.select_frame, text="Next", command=self.copy_files)
        self.next_button.pack(pady=20)

    def choose_directory(self):
        folder_selected = filedialog.askdirectory(initialdir=os.path.expanduser("~/Documents"))
        if folder_selected:
            self.install_path.set(folder_selected)

    def copy_files(self):
        src = os.path.abspath("openweb-ui")
        dest = os.path.join(self.install_path.get(), "openweb-ui")

        if not os.path.exists(src):
            messagebox.showerror("Error", f"The source directory '{src}' does not exist.")
            return

        self.loading_frame = ctk.CTkFrame(self)
        self.loading_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.loading_label = ctk.CTkLabel(self.loading_frame, text="Copying files, please wait...")
        self.loading_label.pack(pady=5)

        self.update()

        try:
            shutil.copytree(src, dest)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while copying files: {e}")
            return

        self.loading_label.configure(text="Files copied successfully!")
        self.loading_frame.after(2000, self.show_image_selection_frame)

    def show_image_selection_frame(self):
        self.select_frame.pack_forget()
        self.loading_frame.pack_forget()

        self.image_selection_frame = ctk.CTkFrame(self)
        self.image_selection_frame.pack(pady=20, padx=20, fill="both", expand=True)

        success_label = ctk.CTkLabel(self.image_selection_frame, text="Code imported successfully!")
        success_label.pack(pady=5)

        image_label = ctk.CTkLabel(self.image_selection_frame, text="Select an image for favicon:")
        image_label.pack(pady=5)

        self.image_buttons = []
        self.image_preview_frame = ctk.CTkFrame(self.image_selection_frame)
        self.image_preview_frame.pack(pady=5)

        for image_file in os.listdir("favicon"):
            image_path = os.path.join("favicon", image_file)
            img = Image.open(image_path)
            img = img.resize((100, 100), Image.LANCZOS)
            photo = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
            self.image_list.append(photo)  # Keep a reference to the image

            image_button = ctk.CTkButton(self.image_preview_frame, image=photo, command=lambda img_path=image_path: self.select_image(img_path))
            image_button.image = photo
            image_button.image_path = image_path
            image_button.pack(side="left", padx=10)
            self.image_buttons.append(image_button)

        self.next_customize_button = ctk.CTkButton(self.image_selection_frame, text="Next", command=self.show_customize_frame)
        self.next_customize_button.pack(pady=20)

    def select_image(self, image_path):
        self.selected_image_path = image_path

        # Highlight selected image
        for button in self.image_buttons:
            if button.image_path == image_path:
                button.configure(border_color="red", border_width=2)
            else:
                button.configure(border_color="white", border_width=0)

        # Copy selected image to target path
        target_path = os.path.join(self.install_path.get(), "openweb-ui/open-webui/static/favicon.png")
        shutil.copyfile(image_path, target_path)

    def show_customize_frame(self):
        self.image_selection_frame.pack_forget()

        self.customize_frame = ctk.CTkFrame(self)
        self.customize_frame.pack(pady=20, padx=20, fill="both", expand=True)

        name_label = ctk.CTkLabel(self.customize_frame, text="Enter a name (max 15 characters):")
        name_label.pack(pady=5)

        self.name_entry = ctk.CTkEntry(self.customize_frame)
        self.name_entry.pack(pady=5)

        self.next_customize_button = ctk.CTkButton(self.customize_frame, text="Next", command=self.apply_customizations)
        self.next_customize_button.pack(pady=20)

    def apply_customizations(self):
        if not self.selected_image_path or not self.name_entry.get():
            messagebox.showerror("Error", "Please select an image and enter a name.")
            return

        new_name = self.name_entry.get()
        file_path = os.path.join(self.install_path.get(), "openweb-ui/open-webui/src/lib/components/chat/Messages/ResponseMessage.svelte")

        # Debug prints to verify paths and file access
        print(f"New name: {new_name}")
        print(f"File path: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")

        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()

            with open(file_path, 'w') as file:
                for i, line in enumerate(lines):
                    if i == 307:
                        file.write(f'{new_name}\n')
                    else:
                        file.write(line)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while modifying the file: {e}")
            return

        npm_path = shutil.which("npm")
        if not npm_path:
            messagebox.showerror("Error", "npm is not installed or not in the system PATH.")
            return

        project_path = os.path.join(self.install_path.get(), "openweb-ui/open-webui")

        print(f"npm path: {npm_path}")
        print(f"Project path: {project_path}")
        print(f"Project path exists: {os.path.exists(project_path)}")

        try:
            self.loading_label = ctk.CTkLabel(self.customize_frame, text="Please wait...")
            self.loading_label.pack(pady=5)
            self.update()

            subprocess.run([npm_path, "install"], cwd=project_path, check=True)
            self.loading_label.configure(text="Building project, please wait...")
            subprocess.run([npm_path, "run", "build"], cwd=project_path, check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"An error occurred during the build process: {e}")
            return

        self.show_settings_frame()

    def show_settings_frame(self):
        self.customize_frame.pack_forget()

        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(pady=20, padx=20, fill="both", expand=True)

        settings_label = ctk.CTkLabel(self.settings_frame, text="Settings")
        settings_label.pack(pady=5)

        modify_image_button = ctk.CTkButton(self.settings_frame, text="Modify Image", command=self.show_image_selection_frame)
        modify_image_button.pack(pady=5)

        modify_name_button = ctk.CTkButton(self.settings_frame, text="Modify Name", command=self.show_customize_frame)
        modify_name_button.pack(pady=5)

        finalize_button = ctk.CTkButton(self.settings_frame, text="Finalize Installation", command=self.finalize_installation)
        finalize_button.pack(pady=20)

        self.server_button = ctk.CTkButton(self.settings_frame, text="Démarrer le serveur", fg_color="red", command=self.toggle_server)
        self.server_button.pack(pady=20)
        self.server_running = False

    def finalize_installation(self):
        backend_path = os.path.join(self.install_path.get(), "openweb-ui/open-webui/backend")

        self.loading_label = ctk.CTkLabel(self.settings_frame, text="Finalizing installation, please wait...")
        self.loading_label.pack(pady=5)

        self.update()

        try:
            subprocess.run(["python", "-m", "venv", "env"], cwd=backend_path, check=True)
            activate_script = os.path.join(backend_path, "env", "Scripts", "activate")
            self.loading_label.configure(text="Veuillez patienter, l'installation peut prendre plusieurs minutes...")
            libs_path = os.path.join(backend_path, "libs")
            requirements_path = os.path.join(backend_path, "requirements.txt")

           # Utilisation de Popen pour exécuter la commande de manière asynchrone
            process = subprocess.Popen([activate_script, "&&", "pip", "install", "--no-index", f"--find-links={libs_path}", "-r", requirements_path], shell=True)

        # Attendre que le processus se termine
            process.wait()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during the package installation: {e}")
        return

        self.loading_label.configure(text="Packages installed successfully!")
        self.show_settings_frame()

    def toggle_server(self):
        if not self.server_running:
            backend_path = os.path.join(self.install_path.get(), "openweb-ui/open-webui/backend")
            activate_script = os.path.join(backend_path, "env", "Scripts", "activate")
            dev_script = os.path.join(backend_path, "env", "Scripts", "dev")

            self.server_button.configure(text="Eteindre le serveur")
            self.server_button.configure(fg_color="green")
            self.loading_label.configure(text="Starting the server, please wait...")
            self.update()

            try:
                subprocess.Popen(["cd {backend_path} && source {activate_script} && cd../.. && ./dev"])
                self.server_running = True
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while starting the server: {e}")
        else:
            # Code to stop the server if needed
            pass


if __name__ == "__main__":
    app = DeploymentTool()
    app.mainloop()
