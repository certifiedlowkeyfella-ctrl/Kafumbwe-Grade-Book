import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

# Initialize the database and create tables if they don't exist
def init_db():
    conn = sqlite3.connect("gradesystem.db")
    cursor = conn.cursor()
    # Create Student table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Student (
        StudentID INTEGER PRIMARY KEY AUTOINCREMENT,
        ExamNumber TEXT UNIQUE,
        Name TEXT,
        ClassID TEXT
    )
    """)
    # Create Results table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Results (
        ResultID INTEGER PRIMARY KEY AUTOINCREMENT,
        StudentID INTEGER,
        Subject TEXT,
        Score INTEGER,
        Term TEXT,
        FOREIGN KEY(StudentID) REFERENCES Student(StudentID)
    )
    """)
    conn.commit()
    conn.close()

class GradeServer(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed_path.query)

        if parsed_path.path == "/":
            self.show_home()
        elif parsed_path.path == "/teacher":
            self.show_teacher_panel()
        elif parsed_path.path == "/add_results":
            self.process_add_results(params)
        elif parsed_path.path == "/view_results":
            self.show_view_results_form(params)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")
    
    def show_home(self):
        html = """
        <html>
        <head>
            <title>Kafumbwe Grade Book Home</title>
            <style>
                body { font-family: Arial, sans-serif; background-color: #f0f4f8; margin: 0; padding: 20px; }
                h2 { color: #333; }
                a { display: block; margin: 10px 0; font-size: 18px; color: #0066cc; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h2>Welcome to Kafumbwe Grade Book.</h2>
            <a href="/teacher">Teacher Panel - Add Results</a>
            <a href="/view_results">Student View Results</a>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def show_teacher_panel(self):
        html = """
        <html>
        <head>
            <title>Teacher - Add Results</title>
            <style>
                body { font-family: Arial, sans-serif; background-color: #f0f4f8; margin: 0; padding: 20px; }
                h2 { color: #333; }
                form { background: #fff; padding: 20px; border-radius: 8px; max-width: 500px; margin: auto; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
                label { display: block; margin-top: 10px; font-weight: bold; }
                input[type=text] { width: 100%; padding: 8px; margin-top: 4px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }
                input[type=submit] { margin-top: 15px; padding: 10px 20px; background-color: #0066cc; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
                input[type=submit]:hover { background-color: #004999; }
                a { display: inline-block; margin-top: 20px; text-decoration: none; color: #0066cc; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h2>Teacher - Add Results</h2>
            <form method="get" action="/add_results">
                <label>Exam Number:</label>
                <input type="text" name="exam_number" required/>

                <label>Name:</label>
                <input type="text" name="name" required/>

                <label>Class:</label>
                <input type="text" name="class_id" required/>

                <label>Subjects and Scores (comma separated):</label>
                <input type="text" name="subject" placeholder="Subject1,Subject2"/>

                <label>Scores (comma separated):</label>
                <input type="text" name="score" placeholder="Score1,Score2"/>

                <input type="submit" value="Add Results"/>
            </form>
            <a href="/">Back to Home</a>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def process_add_results(self, params):
        exam_number = params.get("exam_number", [""])[0]
        name = params.get("name", [""])[0]
        class_id = params.get("class_id", [""])[0]
        subjects_str = params.get("subject", [""])[0]
        scores_str = params.get("score", [""])[0]
        subjects = [s.strip() for s in subjects_str.split(",") if s.strip()]
        scores = [s.strip() for s in scores_str.split(",") if s.strip()]

        if len(subjects) != len(scores):
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Number of subjects and scores do not match.")
            return

        conn = sqlite3.connect("gradesystem.db")
        cursor = conn.cursor()

        cursor.execute("SELECT StudentID FROM Student WHERE ExamNumber=?", (exam_number,))
        row = cursor.fetchone()
        if row:
            student_id = row[0]
        else:
            cursor.execute("INSERT INTO Student (ExamNumber, Name, ClassID) VALUES (?, ?, ?)",
                           (exam_number, name, class_id))
            student_id = cursor.lastrowid

        for subj, score in zip(subjects, scores):
            cursor.execute("INSERT INTO Results (StudentID, Subject, Score, Term) VALUES (?, ?, ?, ?)",
                           (student_id, subj, int(score), "Term 1"))
        conn.commit()
        conn.close()

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def show_view_results_form(self, params):
        html = """
        <html>
        <head>
            <title>Student - View Results</title>
            <style>
                body { font-family: Arial, sans-serif; background-color: #f0f4f8; margin: 0; padding: 20px; }
                h2 { color: #333; }
                form { background: #fff; padding: 20px; border-radius: 8px; max-width: 500px; margin: auto; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
                label { display: block; margin-top: 10px; font-weight: bold; }
                input[type=text] { width: 100%; padding: 8px; margin-top: 4px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }
                input[type=submit] { margin-top: 15px; padding: 10px 20px; background-color: #0066cc; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
                input[type=submit]:hover { background-color: #004999; }
                a { display: inline-block; margin-top: 20px; text-decoration: none; color: #0066cc; }
                a:hover { text-decoration: underline; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { padding: 8px; border: 1px solid #ccc; text-align: left; }
                th { background-color: #e0e0e0; }
            </style>
        </head>
        <body>
            <h2>View Your Results</h2>
            <form method="get" action="/view_results">
                <label>Enter Exam Number:</label>
                <input type="text" name="exam_number" required />

                <label>Enter Class:</label>
                <input type="text" name="class_id" required />

                <input type="submit" value="View Results" />
            </form>
        """

        # If parameters provided, fetch and display results
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
                    total_score = sum(score for _, score in results)
                    count = len(results)
                    average_score = total_score / count if count > 0 else 0
                    status = "Passed" if average_score >= 40 else "Failed"
                    table = "<table><tr><th>Subject</th><th>Score</th></tr>"
                    for subj, score in results:
                        table += f"<tr><td>{subj}</td><td>{score}</td></tr>"
                    table += "</table>"
                    table += f"<h4>Status: {status}</h4>"
                else:
                    table = "<p>No results found for this student.</p>"
            else:
                table = "<p>Student not found. Please check your exam number and class.</p>"
            conn.close()

            html += "<h3>Your Results:</h3>" + table

        html += """
            <a href="/">Back to Home</a>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

def run(server_class=HTTPServer, handler_class=GradeServer, port=3000):
    server_address = ('localhost', 3000)
    print(f"Starting server at http://localhost:{3000}")
    init_db()  # Initialize database before starting server
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == "__main__":
    run()