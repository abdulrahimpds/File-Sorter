import os
import time
import shutil
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

def sort_file(file_path):
    filename = os.path.basename(file_path)
    _, extension = os.path.splitext(filename)
    extension = extension.lower()
    # Check if the file extension exists in the mapping
    if extension in extension_to_folder:
        # Get the destination folder for the file
        folder_name = extension_to_folder[extension]
        destination_folder = os.path.join(download_directory, folder_name)

        # Create the destination folder if it doesn't exist
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        # Move the file to the destination folder
        destination_file = os.path.join(destination_folder, filename)
        # Add a delay before moving the file
        time.sleep(1)
        try:
            shutil.move(file_path, destination_file)
        except Exception as e:
            print(f"Error moving file '{filename}': {str(e)}")

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        # Only process new files
        if not event.is_directory:
            sort_file(event.src_path)

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
    tray_icon = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
    image = Image.open(tray_icon)

    # Create a function that will be called when the user clicks on the icon
    def exit_action(icon, item):
        icon.stop()
        os._exit(0)  # this is a hard exit, consider a cleaner exit if needed

    # Create a menu for the icon
    menu = (pystray.MenuItem('Exit', exit_action),)

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
    # Start main function in a separate thread
    main_thread = Thread(target=failsafe_restart, args=(main_func,))
    main_thread.start()

    # Start the system tray icon in the main thread
    start_tray_icon()
