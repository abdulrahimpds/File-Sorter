import os
import sys
import json
import time
import shutil
import requests
import webbrowser
from threading import Thread
from PIL import Image  # required for pystray
import pystray
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Dictionary mapping file extensions to folder names
extension_to_folder = {
    # Documents
    '.pdf': 'Documents', '.doc': 'Documents', '.docx': 'Documents', '.xls': 'Documents',
    '.xlsx': 'Documents', '.ppt': 'Documents', '.pptx': 'Documents', '.txt': 'Documents',
    '.csv': 'Documents', '.rtf': 'Documents', '.odt': 'Documents', '.ods': 'Documents',
    '.odp': 'Documents', '.epub': 'Documents', '.log': 'Documents',
    
    # Programs
    '.exe': 'Programs', '.msi': 'Programs', '.dmg': 'Programs', '.pkg': 'Programs',
    '.apk': 'Programs',
    
    # Scripts
    '.bat': 'Scripts', '.sh': 'Scripts', '.py': 'Scripts', '.js': 'Scripts', 
    '.html': 'Scripts', '.css': 'Scripts', '.php': 'Scripts', '.java': 'Scripts',
    '.cpp': 'Scripts', '.c': 'Scripts', '.rb': 'Scripts', '.pl': 'Scripts',
    
    # Video
    '.mp4': 'Video', '.avi': 'Video', '.mkv': 'Video', '.mov': 'Video', 
    '.wmv': 'Video', '.flv': 'Video', '.m4v': 'Video', '.mpg': 'Video',
    '.mpeg': 'Video', '.3gp': 'Video', '.3g2': 'Video', 
    
    # Images
    '.jpg': 'Images', '.jpeg': 'Images', '.png': 'Images', '.gif': 'Images',
    '.bmp': 'Images', '.svg': 'Images', '.tiff': 'Images', '.ico': 'Images', 
    '.jfif': 'Images', '.webp': 'Images',
    
    # Music
    '.mp3': 'Music', '.wav': 'Music', '.ogg': 'Music', '.flac': 'Music', 
    '.aac': 'Music', '.m4a': 'Music', '.raw': 'Music', '.wma': 'Music', '.midi': 'Music',
    
    # Compressed
    '.zip': 'Compressed', '.rar': 'Compressed', '.7z': 'Compressed', '.iso': 'Compressed', 
    '.gz': 'Compressed', '.tar': 'Compressed', '.bz2': 'Compressed', '.xz': 'Compressed', 
    '.tar.gz': 'Compressed', '.tgz': 'Compressed'
}

# Path to the user's download directory
download_directory = os.path.expanduser('~/Downloads')

def get_install_dir():
    """Get the directory where the script or executable is located."""
    if getattr(sys, 'frozen', False):  # If running as a compiled executable
        install_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'File Sorter')
        os.makedirs(install_dir, exist_ok=True)
        return install_dir
    else:
        return os.path.dirname(os.path.abspath(__file__))

def update_local_mappings():
    """Update the local mappings file from GitHub every time, preserving original formatting."""
    install_dir = get_install_dir()
    local_mappings_path = os.path.join(install_dir, 'mapping.json')
    url = "https://raw.githubusercontent.com/abdulrahimpds/File-Sorter/main/mapping.json"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            remote_json = response.text  # Get the raw text of the response

            with open(local_mappings_path, 'w') as file:
                file.write(remote_json)  # Write the raw text to the file
            print("Local mappings updated.")
        else:
            print("Failed to fetch remote mappings; using local version if available.")
    except requests.RequestException as e:
        print(f"Network error when attempting to update mappings; using local version if available. Error: {e}")

def get_folder_for_extension(extension):
    """Fetch the destination folder for a file type from local JSON mappings if not recognized by the hardcoded mappings."""
    # Ensure we are consistently using the script's directory for JSON file location
    install_dir = get_install_dir()
    local_mappings_path = os.path.join(install_dir, 'mapping.json')

    try:
        with open(local_mappings_path, 'r') as file:
            json_mappings = json.load(file)
        return json_mappings.get(extension)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def sort_file(file_path):
    filename = os.path.basename(file_path)
    _, extension = os.path.splitext(filename)
    extension = extension.lower()

    # First try to get the folder name using the hardcoded dictionary
    folder_name = extension_to_folder.get(extension)

    # If not found in the hardcoded dictionary, check the JSON mappings
    if not folder_name:
        folder_name = get_folder_for_extension(extension)

    # Proceed if a folder name was determined
    if folder_name:
        destination_folder = os.path.join(download_directory, folder_name)
        os.makedirs(destination_folder, exist_ok=True)  # Ensure the folder exists
        destination_file = os.path.join(destination_folder, filename)

        # Move the file with retries if the file is in use
        while os.path.exists(file_path):  # While the source file exists
            try:
                shutil.move(file_path, destination_file)
                print(f"Moved '{filename}' to '{destination_folder}'")
                break  # Successfully moved the file
            except Exception as e:
                if 'being used by another process' in str(e):
                    print(f"File '{filename}' is in use. Retrying...")
                    time.sleep(2)  # Wait before trying again
                else:
                    print(f"Stopped trying to move file '{filename}' due to error: {str(e)}")
                    break

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        # Only process new files
        if not event.is_directory:
            time.sleep(0.3)
            sort_file(event.src_path)

    def on_moved(self, event):
        # Only process new files
        if not event.is_directory:
            time.sleep(0.3)
            sort_file(event.dest_path)

def main_func():
    # Perform initial sorting
    for filename in os.listdir(download_directory):
        file_path = os.path.join(download_directory, filename)
        if os.path.isfile(file_path):
            sort_file(file_path)
            
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, download_directory, recursive=False)
    
    # Start the observer in a separate thread
    observer_thread = Thread(target=observer.start)
    observer_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def start_tray_icon():
    # Load an image for the icon (this should be 64x64 pixels for best compatibility)
    tray_icon = os.path.join(os.path.dirname(os.path.abspath(__file__)), '128.ico')
    image = Image.open(tray_icon)

    def open_extension_url():
        webbrowser.open('https://chrome.google.com/webstore/detail/file-sorter/bnckpomjfdfppkaelickhdgmmmacheac')

    # Create a function that will be called when the user clicks on the icon
    def exit_action(icon, item):
        icon.stop()
        os._exit(0)  # this is a hard exit, consider a cleaner exit if needed

    # Create a menu for the icon
    menu = (
        pystray.MenuItem('Need Web Extension?', open_extension_url),
        pystray.MenuItem('Exit', exit_action),
    )

    # Create the system tray icon
    icon = pystray.Icon("File Sorter", image, "File Sorter", menu)

    # Run the system tray icon
    icon.run()

def failsafe_restart(func, *args, **kwargs):
    while True:
        try:
            func(*args, **kwargs)
            time.sleep(1)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Restarting the program...")
            # If you want to limit the number of restarts, you can add a counter here.
            continue
        break

if __name__ == "__main__":
    # Check and update local mappings
    update_local_mappings()

    # Start main function in a separate thread
    main_thread = Thread(target=failsafe_restart, args=(main_func,))
    main_thread.start()

    # Start the system tray icon in the main thread
    start_tray_icon()
