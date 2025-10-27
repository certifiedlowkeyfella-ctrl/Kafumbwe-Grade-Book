# Kafumbwe Grade Book System

A simple Python HTTP server using SQLite to manage and view student results.

## Features

- Teachers can add results for students.
- Students can view their results by exam number and class.
- Basic authentication (teacher/pupil roles in `How.py` version).

## Requirements

- Python 3.x (tested with Python 3.8+)
- No extra libraries needed (`sqlite3` and `http.server` are standard).

## Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/kafumbwe-grade-book.git
   cd kafumbwe-grade-book
   ```

2. **Run the server:**
   - For the simple version:
     ```bash
     python viewResults.py
     ```
   - For the version with login:
     ```bash
     python How.py
     ```

3. **Open your browser and go to:**  
   [http://localhost:3000](http://localhost:3000)

## Notes

- The database (`gradesystem.db`) will be created automatically.
- To reset data, delete `gradesystem.db` and restart the server.

---
