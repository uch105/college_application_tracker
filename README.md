# README: Professor Application Tracker

## Overview
This is a desktop application built with Python and PyQt5 for tracking professor applications. It includes features like database management, search functionality with fuzzy matching, filtering options, and data visualization.

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

## Installation & Setup

### 1. Clone or Download the Project
```bash
# If using git
git clone <repository-url>
cd college_application_tracker

# Or simply download and extract the project files
```

### 2. Set Up Virtual Environment

#### On Windows:
```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### On Linux:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Application

#### On Windows:
```cmd
python main.py
```

#### On Linux:
```bash
python3 main.py
```

## Creating an Executable

### For Windows (.exe with icon)

1. Install PyInstaller:
```cmd
pip install pyinstaller
```

2. Create a spec file (optional) or run directly:
```cmd
pyinstaller --onefile --windowed --icon=icon.ico --name "ProfessorTracker" main.py
```

3. The executable will be in the `dist` folder

### For Linux (.sh file)

1. Create a shell script `run_professor_tracker.sh`:
```bash
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 main.py
```

2. Make the script executable:
```bash
chmod +x run_professor_tracker.sh
```

3. Run the application:
```bash
./run_professor_tracker.sh
```

## File Structure
```
professor-application-tracker/
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── icon.ico            # Application icon (for Windows)
├── run_professor_tracker.sh  # Linux shell script
├── README.md           # This file
```

## Requirements File
Create a `requirements.txt` file with the following content:
```
fuzzywuzzy==0.18.0
Levenshtein==0.27.1
PyQt5==5.15.11
PyQt5-Qt5==5.15.17
PyQt5_sip==12.17.0
PyQtChart==5.15.7
PyQtChart-Qt5==5.15.17
python-Levenshtein==0.27.1
RapidFuzz==3.14.1 # Only needed if creating executables
```

## Database Location
The application automatically creates and uses a SQLite database at:
- Linux: `/var/personal/db/professor_applications.db`
- Windows: The application may need write permissions to create this directory

If you encounter permission issues on Linux, you may need to:
```bash
sudo mkdir -p /var/personal/db
sudo chmod 777 /var/personal/db
```

Alternatively, you can modify the `db_dir` path in the code to use a user-writable location.

## Features
- ✅ Database creation and management
- ✅ Add, edit, and delete applications
- ✅ Search with fuzzy matching for emails
- ✅ Filter by status, response, university, and professor
- ✅ Country-wise pie chart visualization
- ✅ Clean, elegant UI

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'PyQt5'**
   - Solution: Make sure you've activated the virtual environment and run `pip install -r requirements.txt`

2. **Permission denied errors on Linux**
   - Solution: Ensure the database directory exists and has proper permissions

3. **Fuzzy matching not working**
   - Solution: Install the `python-levenshtein` package for better performance

4. **Application won't start on Windows**
   - Solution: Try running as Administrator if there are file permission issues

### Getting Help
If you encounter issues not covered here, please check:
- All dependencies are installed correctly
- You're using a supported Python version (3.8+)
- You have write permissions to the database directory

## License
This project is for educational/demonstration purposes.
