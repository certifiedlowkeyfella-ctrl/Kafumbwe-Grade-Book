import sqlite3
import http.server
import socketserver
import urllib.parse

# Initialize database with tables for Teachers, Classes, Students, Results
def init_db():
    conn = sqlite3.connect("gradesystem.db")
    cursor = conn.cursor()

    # Drop tables if they exist
    cursor.executescript("""
    DROP TABLE IF EXISTS Teachers;
    DROP TABLE IF EXISTS Class;
    DROP TABLE IF EXISTS Student;
    DROP TABLE IF EXISTS Results;
    """)

    # Create tables in specified order
    cursor.execute("""
    -- Teachers table
    CREATE TABLE Teachers (
        UserID INTEGER PRIMARY KEY AUTOINCREMENT,
        Username TEXT UNIQUE,
        Password TEXT,
        Role TEXT -- 'teacher' or 'pupil'
    );
    """)
    cursor.execute("""
    -- Classes table
    CREATE TABLE Class (
        ClassID INTEGER PRIMARY KEY AUTOINCREMENT,
        ClassName TEXT UNIQUE
    );
    """)
    cursor.execute("""
    -- Students table
    CREATE TABLE Student (
        StudentID INTEGER PRIMARY KEY AUTOINCREMENT,
        ExamNumber TEXT,
        Name TEXT,
        ClassID INTEGER,
        FOREIGN KEY (ClassID) REFERENCES Class(ClassID)
    );
    """)
    cursor.execute("""
    -- Results table
    CREATE TABLE Results (
        ResultID INTEGER PRIMARY KEY AUTOINCREMENT,
        StudentID INTEGER,
        Subject TEXT,
        Score INTEGER,
        Term TEXT,
        FOREIGN KEY (StudentID) REFERENCES Student(StudentID)
    );
    """)

    # Insert sample data
    cursor.execute("INSERT OR IGNORE INTO Teachers (Username, Password, Role) VALUES ('teacher1', 'pass123', 'teacher')")
    cursor.execute("INSERT OR IGNORE INTO Teachers (Username, Password, Role) VALUES ('teacher2', 'pass123', 'teacher')")
    cursor.execute("INSERT OR IGNORE INTO Teachers (Username, Password, Role) VALUES ('teacher3', 'pass123', 'teacher')")

    cursor.execute("INSERT OR IGNORE INTO Class (ClassName) VALUES ('Form 1')")
    cursor.execute("INSERT OR IGNORE INTO Class (ClassName) VALUES ('Form 2')")

    cursor.execute("INSERT OR IGNORE INTO Student (ExamNumber, Name, ClassID) VALUES ('EXAM001', 'Alice', 1)")
    cursor.execute("INSERT OR IGNORE INTO Student (ExamNumber, Name, ClassID) VALUES ('EXAM002', 'Bob', 2)")
    cursor.execute("INSERT OR IGNORE INTO Student (ExamNumber, Name, ClassID) VALUES (170900600401, 'Jimmy Sakala', 'KB3')")
    cursor.execute("INSERT OR IGNORE INTO Student (ExamNumber, Name, ClassID) VALUES (2023021197, 'James Sakala', 'KB2')")

    cursor.execute("INSERT OR IGNORE INTO Results (StudentID, Subject, Score, Term) VALUES (1, 'Math', 85, 'Term 1')")
    cursor.execute("INSERT OR IGNORE INTO Results (StudentID, Subject, Score, Term) VALUES (1, 'English', 78, 'Term 1')")
    cursor.execute("INSERT OR IGNORE INTO Results (StudentID, Subject, Score, Term) VALUES (2, 'Math', 92, 'Term 1')")
    cursor.execute("INSERT OR IGNORE INTO Results (StudentID, Subject, Score, Term) VALUES (2, 'English', 88, 'Term 1')")

    conn.commit()
    conn.close()

# Helper function to generate styled HTML with background
def get_html(content):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>KAFUMBWE GRADE BOOK SYSTEM</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #74ebd5 0%, #ACB6E5 100%);
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 900px;
                margin: auto;
                background: rgba(255, 255, 255, 0.9);
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.2);
            }}
            h1 {{
                text-align: center;
                margin-bottom: 30px;
                color: #333;
                font-family: 'Arial Rounded MT Bold', cursive;
            }}
            a {{
                display: inline-block;
                margin-top: 15px;
                padding: 10px 20px;
                background-color: #4CAF50;
                color: #fff;
                border-radius: 8px;
                text-decoration: none;
                font-weight: bold;
                transition: background-color 0.3s ease;
            }}
            a:hover {{
                background-color: #45a049;
            }}
            form {{
                background: #fff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }}
            label {{
                display: block;
                margin-top: 15px;
                font-weight: 600;
                color: #555;
            }}
            input[type=text], input[type=password], select, input[type=number] {{
                width: 100%; box-sizing: border-box;
                padding: 12px 15px;
                margin-top: 8px;
                border: 2px solid #ccc;
                border-radius: 6px;
                font-size: 1em;
                transition: border-color 0.2s;
            }}
            input[type=text]:focus, input[type=password]:focus, select:focus, input[type=number]:focus {{
                border-color: #4CAF50;
                outline: none;
            }}
            input[type=submit] {{
                margin-top: 20px;
                padding: 12px 25px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1.1em;
                transition: background-color 0.3s ease;
            }}
            input[type=submit]:hover {{
                background-color: #45a049;
            }}
            /* Styling table for results */
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 25px;
            }}
            th, td {{
                padding: 14px;
                border: 1px solid #ddd;
                text-align: center;
                border-radius: 4px;
            }}
            th {{
                background-color: #f2f2f2;
                font-weight: 600;
            }}
            /* Buttons inside results table (if any) */
            .btn {{
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.9em;
                margin: 2px;
            }}
            .edit-btn {{
                background-color: #2196F3;
                color: white;
            }}
            .delete-btn {{
                background-color: #f44336;
                color: white;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>KAFUMBWE GRADE BOOK SYSTEM</h1>
            {content}
        </div>
    </body>
    </html>
    """

# Basic server handler
class GradeSystemHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed_path.query)
        path = parsed_path.path

        if path == "/":
            self.show_login()
        elif path == "/dashboard":
            self.show_dashboard()
        elif path == "/view_results":
            self.view_results(params)
        elif path == "/teacher":
            self.show_teacher_page(params)
        elif path == "/logout":
            self.show_login()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"<h1>404 Not Found</h1>")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data = urllib.parse.parse_qs(self.rfile.read(length).decode())

        path = self.path

        if path == "/login":
            self.handle_login(data)
        elif path == "/teacher/add_results":
            self.process_add_results(data)
        elif path.startswith("/teacher/edit_result"):
            self.edit_result(data, path)
        elif path == "/teacher/delete_result":
            self.delete_result(data)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"<h1>404 Not Found</h1>")

    def show_login(self):
        html = get_html("""
            <h2 style="text-align:center;">Login</h2>
            <form method="post" action="/login">
                <label>Username:</label>
                <input type="text" name="username" required />
                <label>Password:</label>
                <input type="password" name="password" required />
                <input type="submit" value="Login" />
            </form>
        """)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def handle_login(self, data):
        username = data.get("username", [""])[0]
        password = data.get("password", [""])[0]
        conn = sqlite3.connect("gradesystem.db")
        cursor = conn.cursor()
        cursor.execute("SELECT Role FROM Teachers WHERE Username=? AND Password=?", (username, password))
        row = cursor.fetchone()
        conn.close()
        if row:
            role = row[0]
            if role == "teacher":
                self.send_response(302)
                self.send_header("Location", "/teacher")
                self.end_headers()
            elif role == "pupil":
                self.send_response(302)
                self.send_header("Location", "/view_results")
                self.end_headers()
        else:
            self.show_login()

    def show_teacher_page(self, params):
        # Extract class options
        conn = sqlite3.connect("gradesystem.db")
        classes = conn.execute("SELECT ClassID, ClassName FROM Class").fetchall()
        conn.close()
        options = "".join([f'<option value="{c[0]}">{c[1]}</option>' for c in classes])

        html_content = f"""
            <h2>Teacher Dashboard</h2>
            <a href="/dashboard">View Dashboard</a>
            <h3 style="margin-top:30px;">Add Results for Student</h3>
            <form method="post" action="/teacher/add_results">
                <label>Exam Number:</label>
                <input type="text" name="exam_number" required />

                <label>Name:</label>
                <input type="text" name="name" required />

                <label>Class:</label>
                <select name="class_id" required>
                    {options}
                </select>

                <h4 style="margin-top:20px;">Add Results:</h4>
                <div id="results-container" style="margin-top:15px;">
                    <div class="result-entry" style="margin-bottom:10px;">
                        <input type="text" name="subject[]" placeholder="Subject" required style="width:45%; margin-right:10px; padding:8px; border-radius:4px; border:1px solid #ccc;"/>
                        <input type="number" name="score[]" placeholder="Score" min="0" max="100" required style="width:20%; margin-right:10px; padding:8px; border-radius:4px; border:1px solid #ccc;"/>
                        <button type="button" onclick="this.parentElement.remove()" style="background:#f44336; color:#fff; border:none; padding:8px 12px; border-radius:4px; cursor:pointer;">Remove</button>
                        <button type="button" onclick="alert('Update logic goes here')" style="background:#2196F3; color:#fff; border:none; padding:8px 12px; border-radius:4px; cursor:pointer; margin-left:6px;">Update</button>
                    </div>
                </div>
                <button type="button" onclick="addResult()" style="margin-top:10px; padding:8px 16px; border:none; border-radius:4px; background:#2196F3; color:#fff; cursor:pointer;">Add Another Result</button>
                <br/><br/>
                <input type="submit" value="Save Results" style="background:#4CAF50; padding:10px 20px; border:none; border-radius:4px; color:#fff; font-size:1em; cursor:pointer;"/>
            </form>
            <script>
                function addResult() {{
                    const container = document.getElementById('results-container');
                    const div = document.createElement('div');
                    div.className = 'result-entry';
                    div.style.marginBottom = '10px';
                    div.innerHTML = `
                        <input type="text" name="subject[]" placeholder="Subject" required style="width:45%; margin-right:10px; padding:8px; border-radius:4px; border:1px solid #ccc;"/>
                        <input type="number" name="score[]" placeholder="Score" min="0" max="100" required style="width:20%; margin-right:10px; padding:8px; border-radius:4px; border:1px solid #ccc;"/>
                        <button type="button" onclick="this.parentElement.remove()" style="background:#f44336; color:#fff; border:none; padding:8px 12px; border-radius:4px; cursor:pointer;">Remove</button>
                        <button type="button" onclick="alert('Update logic goes here')" style="background:#2196F3; color:#fff; border:none; padding:8px 12px; border-radius:4px; cursor:pointer; margin-left:6px;">Update</button>
                    `;
                    container.appendChild(div);
                }}
            </script>
            <br/><a href="/logout" style="display:inline-block; margin-top:20px;">Logout</a>
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(get_html(html_content).encode())

    def process_add_results(self, data):
        exam_number = data.get("exam_number", [""])[0]
        name = data.get("name", [""])[0]
        class_id = data.get("class_id", [""])[0]
        subjects = data.get("subject[]", [])
        scores = data.get("score[]", [])
        if len(subjects) != len(scores):
            # Could add error message here
            self.show_teacher_page({})
            return
        conn = sqlite3.connect("gradesystem.db")
        cursor = conn.cursor()
        # Check if student exists
        cursor.execute("SELECT StudentID FROM Student WHERE ExamNumber=?", (exam_number,))
        row = cursor.fetchone()
        if row:
            student_id = row[0]
        else:
            cursor.execute("INSERT INTO Student (ExamNumber, Name, ClassID) VALUES (?, ?, ?)", (exam_number, name, class_id))
            student_id = cursor.lastrowid
        # Insert results
        for subj, score in zip(subjects, scores):
            cursor.execute("INSERT INTO Results (StudentID, Subject, Score, Term) VALUES (?, ?, ?, ?)",
                           (student_id, subj, int(score), "Term 1"))
        conn.commit()
        conn.close()
        self.send_response(302)
        self.send_header("Location", "/teacher")
        self.end_headers()

    def view_results(self, params):
        # Show form for students to enter exam number and class
        html = """
            <h2>View Your Results</h2>
            <form method="get" action="/view_results" style="margin-top:20px;">
                <label>Enter Exam Number:</label>
                <input type="text" name="exam_number" required style="width:100%; padding:8px; border-radius:4px; border:1px solid #ccc;"/>
                <label style="margin-top:15px;">Select Class:</label>
                <select name="class_id" required style="width:100%; padding:8px; border-radius:4px; border:1px solid #ccc;">
                    {options}
                </select>
                <br/><br/>
                <input type="submit" value="View Results" style="background:#4CAF50; padding:10px 20px; border:none; border-radius:4px; color:#fff; font-size:1em; cursor:pointer;"/>
            </form>
        """
        # Populate class options
        conn = sqlite3.connect("gradesystem.db")
        classes = conn.execute("SELECT ClassID, ClassName FROM Class").fetchall()
        conn.close()
        options = "".join([f'<option value="{c[0]}">{c[1]}</option>' for c in classes])
        html = html.replace("{options}", options)

        # If parameters provided, show results
        if "exam_number" in params and "class_id" in params:
            exam_number = params["exam_number"][0]
            class_id = params["class_id"][0]
            conn = sqlite3.connect("gradesystem.db")
            cursor = conn.cursor()
            cursor.execute("SELECT StudentID FROM Student WHERE ExamNumber=? AND ClassID=?", (exam_number, class_id))
            row = cursor.fetchone()
            if row:
                student_id = row[0]
                cursor.execute("SELECT Subject, Score FROM Results WHERE StudentID=?", (student_id,))
                results = cursor.fetchall()
                if results:
                    table_html = "<table><tr><th>Subject</th><th>Score</th></tr>"
                    for subj, score in results:
                        table_html += f"<tr><td>{subj}</td><td>{score}</td></tr>"
                    table_html += "</table>"
                else:
                    table_html = "<p>No results found for this student.</p>"
            else:
                table_html = "<p>Student not found. Please check your exam number and class.</p>"
            conn.close()
            html += "<h3 style='margin-top:30px;'>Your Results:</h3>" + table_html

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(get_html(html).encode())

# Initialize database and run server
def main():
    init_db()
    PORT = 3000
    with socketserver.TCPServer(("", PORT), GradeSystemHandler) as server:
        print(f"Server running at http://localhost:{3000}")
        print("Open your browser and visit that URL.")
        server.serve_forever()

if __name__ == "__main__":
    main()