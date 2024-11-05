# SnapBridge

SnapBridge is a Windows application and iOS shortcut that lets you automatically transfer photos and videos from your iPhone to your Windows PC over a local network connection. It includes a server that runs on Windows, receives media as POST requests from the iPhone, and saves the files on your computer. The application runs in the system tray, where you can easily configure settings, open the IP display window, and access other options.

---

## Table of Contents
1. [Features](#features)
2. [Installation](#installation)
3. [Setup Instructions](#setup-instructions)
4. [iPhone Shortcut Setup](#iphone-shortcut-setup)
5. [Usage](#usage)
6. [How It Works](#how-it-works)
7. [Compiling the Application](#compiling-the-application)
8. [License](#license)

---

## Features
- Automatically transfers the latest photo or video taken on your iPhone to a specified folder on your PC.
- Displays a Windows notification when new media is received.
- Adds itself to Windows startup automatically to run every time you log in.
- Allows easy configuration of save path and settings through a settings window.
- Runs in the background as a system tray application for easy access.

## Installation
To install SnapBridge on your PC:
1. **Download**: You can download the precompiled `.exe` from the GitHub packages in this repository.
2. **Run the Application**: Execute `SnapBridge.exe` to start the server. It will automatically add itself to Windows startup, so it runs each time you log in.

If you prefer to build it yourself, see the [Compiling the Application](#compiling-the-application) section.

---

## Setup Instructions
1. **First-Time Run**: When you first start SnapBridge, it will open a window showing the IP address and port you need to use on your iPhone. Write this information down, as you’ll need it for the iPhone Shortcut setup.
2. **Settings**:
   - Right-click the tray icon and select "Open Settings" to modify save path or enable/disable automatic file explorer opening.
   - Configure settings for your preferred save path and other options. These will be saved to your local `AppData` folder in a file called `settings.ini`.

---

## iPhone Shortcut Setup

1. **Download the Shortcut**: [SnapBridge Shortcut](https://www.icloud.com/shortcuts/a3c7dc8ff5c948aaabb3521fb746c13a)
   - Add this shortcut to your iPhone’s Shortcuts app. It’s configured to automatically encode your latest photo or video and send it as a POST request to the PC when triggered.

2. **Automation Setup**:
   - Open the **Shortcuts** app on your iPhone.
   - Go to **Automation** > **Create Personal Automation** > **App**.
   - Select **Camera** as the app and set it to trigger **When App Closes**.
   - Under actions, select **Run Shortcut** and choose the SnapBridge shortcut you just added.

3. **Configure the Note**:
   - Open the **Notes** app and create a new note titled **SnapBridge**.
   - Add the IP address and port from Step 1 (e.g., `193.156.764.36:5000`) to this note. The shortcut will automatically retrieve this IP from the note to know where to send your media.

After completing these steps, SnapBridge will be set up to transfer your latest photos or videos every time you close the Camera app.

---

## Usage

- **Run SnapBridge**: Double-click `SnapBridge.exe` (or the compiled `.exe` if you built it yourself) to start the application. 
- **Check IP Address**: If you need to confirm the IP address, right-click the system tray icon and select the option to display the IP.
- **View Notifications**: When a photo or video is received, SnapBridge will display a notification on Windows. Click the notification to save the file to your pc.
- **Modify Settings**: Right-click the tray icon and select "Open Settings" to adjust the save path and other configurations.

---

## How It Works

1. **Windows Server**: A Flask server runs locally on your PC, listening on a specified IP and port (e.g., `193.156.764.36:5000`).
2. **iPhone Shortcut**: The iPhone shortcut retrieves the IP from the note titled **SnapBridge** and uses it to send a POST request to the PC. This POST request includes the latest photo or video in base64-encoded format.
3. **Processing**: When a request is received, SnapBridge decodes the media and saves it to the designated save path on your PC. Notifications are shown on Windows to confirm successful transfers.
4. **Automatic Startup**: The application adds itself to Windows startup when you first run it, so it will automatically launch whenever you log in to your PC.

---

## Compiling the Application

If you want to compile the SnapBridge application yourself, follow these steps:

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   Ensure you have `pyinstaller`, `flask`, and `win10toast_click` installed.

2. **Compile with PyInstaller**:
   Run the following command to build the `.exe` using the provided `.spec` file:
   ```bash
   pyinstaller SnapBridge.spec
   ```
   This will package the application with all necessary files and create a standalone executable in the `dist` folder.

3. **Run the Executable**:
   After compiling, run the generated `SnapBridge.exe` to start the application.

---

## License
SnapBridge is open-source and available under the MIT License. See the `LICENSE` file for more details.
