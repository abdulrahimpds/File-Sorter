# File Sorter

File Sorter is a Python application that helps you keep your Downloads directory clean and organized. It automatically sorts files into specific folders based on their types (extensions).

## Features

- Automatic sorting of files into folders by their type (extension).
- Supports a wide variety of file types including documents, programs, scripts, videos, images, music, and compressed files.
- Runs in the background with a system tray icon.

## Usage

1. Clone this repository to your local machine.
2. Navigate to the directory containing `main.py`.
3. Run `python main.py` to start the program.
4. All files in your Downloads directory will be sorted into respective folders. Any new files added to the Downloads directory will automatically be sorted.

## Dependencies

This program requires the following Python packages:

- `os`
- `time`
- `shutil`
- `threading`
- `PIL` (Pillow)
- `pystray`
- `watchdog`

## Customization

You can customize the types of files the program sorts by modifying the `extension_to_folder` dictionary in `main.py`. The keys of this dictionary are file extensions and the values are the names of the folders into which files with these extensions will be sorted.

## Disclaimer

This program moves files in your Downloads directory. Please ensure that you have backups of important files before running the program. We are not responsible for any lost or misplaced files due to the usage of this program.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
