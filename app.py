from flask import Flask, request, jsonify
from win10toast_click import ToastNotifier
import os
import base64
import configparser
import datetime
import subprocess
import platform
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from PIL import Image
import pystray
from pystray import MenuItem as item
import sys
from win32com.client import Dispatch
import subprocess
import socket 

app = Flask(__name__)
notifier = ToastNotifier()

flask_ip = "0.0.0.0"
flask_port = "5000"

default_settings = {
    "save_path": os.path.join(os.environ["USERPROFILE"], "Pictures", "SnapBridge"),
    "open_explorer": "True"
}

# Determine the base path
if getattr(sys, 'frozen', False):
    # Running in a bundle
    application_path = os.path.dirname(sys.executable)
else:
    # Running in normal Python environment
    application_path = os.path.dirname(os.path.abspath(__file__))

# Use AppData directory for settings
settings_dir = os.path.join(os.getenv('APPDATA'), 'SnapBridge')
os.makedirs(settings_dir, exist_ok=True)
settings_path = os.path.join(settings_dir, 'settings.ini')

config = configparser.ConfigParser()



def add_to_startup():
    # Adds a shortcut of the application to the Windows Startup folder.
    startup_dir = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    shortcut_path = os.path.join(startup_dir, "SnapBridge.lnk")

    # Check if the shortcut already exists
    if not os.path.exists(shortcut_path):
        # Create a shortcut using win32com.client
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortcut(shortcut_path)
        shortcut.TargetPath = sys.executable  # Path to the Python executable or the PyInstaller executable
        shortcut.WorkingDirectory = os.path.dirname(sys.executable)
        shortcut.IconLocation = os.path.join(os.path.dirname(__file__), "icon.ico")  # Optional icon
        shortcut.save()
        print("Added application to startup.")
    else:
        print("Application already in startup folder.")


def load_settings():
    global save_path
    global open_explorer
    if os.path.exists(settings_path):
        config.read(settings_path)
        save_path = os.path.normpath(config["general"]["save_path"])
        open_explorer = config["general"].getboolean("open_explorer")

    else:
        # If settings file doesn't exist, create it with default values
        save_path = default_settings["save_path"]
        open_explorer = default_settings["open_explorer"]
        # Create settings file with default values
        config["general"] = default_settings
        with open(settings_path, 'w') as configfile:
            config.write(configfile)


# Function to get the local IP address
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to an external address (Google's public DNS) to get the local IP
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"  # Fallback to localhost if there is an error
    finally:
        s.close()
    return ip

def show_ip_window():
    ip_address = get_local_ip()
    port = flask_port  
    
    ip_window = tk.Tk()
    ip_window.title("Connect to SnapBridge")
    ip_window.geometry("600x100")
    ip_window.lift()
    ip_window.focus_force()

    tk.Label(ip_window, text=f"Write the following to a Note on your iPhone with the title 'SnapBridge' (without quotes): {ip_address}:{port}", padx=10, pady=10).pack()

    ok_button = tk.Button(ip_window, text="OK", command=lambda: ip_window.destroy(), padx=10, pady=5)
    ok_button.pack(pady=10)  # Add some padding for aesthetics

    ip_window.mainloop()

def check_first_run():
    print(settings_path)
    if not os.path.exists(settings_path):
        print("settins doesnt excist")
        show_ip_window()  # Show the IP window if settings do not exist

def save_settings(new_save_path, new_open_explorer):
    # Save updated Settings to settings.ini
    config["general"]["save_path"] = new_save_path
    config["general"]["open_explorer"] = str(new_open_explorer)
    with open(settings_path, "w") as configfile:
        config.write(configfile)
    # Load settings upon opening the settings file to refresh global variables with new values
    load_settings()
    messagebox.showinfo("Settings Saved", "Your settings have been updated.")

def open_settings_window():
    # Open a Tkinter Window to update Settings
    def save_changes():
        # Update settingsa from the UI fields
        new_save_path = os.path.normpath(path_entry.get())
        new_open_explorer = bool(var_open_explorer.get())
        save_settings(new_save_path, new_open_explorer)
        settings_window.destroy()
    
    settings_window = tk.Tk()
    settings_window.title("Edit Settings")

    icon_path = resource_path("icon.ico")
    settings_window.iconbitmap(icon_path)

    # Bring the settings window to the front and focus on it
    settings_window.lift()
    settings_window.focus_force()

    tk.Label(settings_window, text="Save Path:").grid(row=0, column=0, padx=5, pady=5)
    path_entry = tk.Entry(settings_window, width=50)
    path_entry.insert(0, save_path)
    path_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(settings_window, text="Open Explorer:").grid(row=1, column=0, padx=5, pady=5)
    var_open_explorer = tk.BooleanVar(value=open_explorer)
    tk.Checkbutton(settings_window, variable=var_open_explorer).grid(row=1, column=1, padx=5, pady=5)

    # Button to open directory chooser
    def browse_directory():
        selected_path = filedialog.askdirectory()
        if selected_path:
            path_entry.delete(0, tk.END)
            path_entry.insert(0, selected_path)

    tk.Button(settings_window, text="Browse", command=browse_directory).grid(row=0, column=2, padx=5, pady=5)

    tk.Button(settings_window, text="Save Changes", command=save_changes).grid(row=2, column=0, columnspan=3, pady=10)

    settings_window.mainloop()

def start_flask_server():
    app.run(host=flask_ip, port=flask_port)

def run_server():
    # Run server in background thread
    threading.Thread(target=start_flask_server).start()

def exit_program():
    # Stop the system tray icon
    icon.stop()
    # Exit the application completely, including the Flask server
    os._exit(0)

def resource_path(relative_path):
    # Get absolute path to resource, works for dev and PyInstaller
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # If not running as a bundle, use the normal path
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# System tray setup
icon_image = Image.open(resource_path("icon.ico")) 
menu = (item('Show IP Address', show_ip_window),
        item('Open Settings', open_settings_window),
        item('Exit', exit_program)
)

icon = pystray.Icon("SnapBridge", icon_image, menu=menu)


@app.route("/", methods=["POST"])
def upload_photo():
    print("Received request")
    global image_data
    global media_type
    data = request.json

    if not "data" in data:
        print("user did not include 'data' argument")
        return jsonify({"error": "data argument is required"}), 400
    if not "mediaType" in data:
        print("user did not include 'mediaType' argument")
        return jsonify({"error": "mediaType argument is required"}), 400

    image_data = data["data"] 
    media_type = data["mediaType"]
    print("received image data")
    notifier.show_toast(f"New {media_type} received", "Click to save", 
                        duration=10, callback_on_click=save_photo, icon_path=resource_path("icon.png"))
    return jsonify({"message": "Image received successfully."}), 200

def save_photo():
    if image_data:
        decrypted_image_data = base64.b64decode(image_data)
        
        if media_type not in ["Image", "Video"]:
            print("User passed unsupported media type:", media_type)
            return jsonify({"error": "Unsupported media type"}), 400
        
        # Check which media type is passed in the request and set extension accordingly
        if media_type == "Image":
            extension = ".jpg"
        elif media_type == "Video":
            extension = ".mp4"
        
        current_time = datetime.datetime.now()
        file_name = f"{media_type}_{current_time.strftime('%Y-%m-%d_%H.%M.%S')}{extension}"
        
        file_path = os.path.join(save_path, file_name)
        with open (file_path, "wb") as f:
            f.write(decrypted_image_data)
        print("Media saved succesfully!")

        if open_explorer == True:
            open_file_location(file_path)

def open_file_location(path):
    """Open the file's directory and highlight it on different OSes."""
    system = platform.system()
    if system == "Windows":
        # On Windows, use File Explorer to highlight the file
        subprocess.Popen(f'explorer /select,"{path}"')
    elif system == "Darwin":  # macOS
        # On macOS, use the 'open' command to open Finder
        subprocess.Popen(["open", "-R", path])
    elif system == "Linux":
        # On Linux, try to open the containing folder with xdg-open
        subprocess.Popen(["xdg-open", os.path.dirname(path)])
    else:
        print("Unsupported operating system")


add_to_startup()
check_first_run()
load_settings()
# Start the server and system tray icon
run_server()
icon.run()