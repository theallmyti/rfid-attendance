from flask import Flask, render_template, request, redirect, url_for
import json
from datetime import datetime
import os

app = Flask(__name__)

STUDENTS_FILE = "students.json"
ATTENDANCE_FILE = "attendance.json"

# Ensure JSON files exist
if not os.path.exists(STUDENTS_FILE):
    with open(STUDENTS_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(ATTENDANCE_FILE):
    with open(ATTENDANCE_FILE, "w") as f:
        json.dump([], f)

def load_students():
    with open(STUDENTS_FILE, "r") as f:
        return json.load(f)

def save_students(students):
    with open(STUDENTS_FILE, "w") as f:
        json.dump(students, f, indent=4)

def load_attendance():
    with open(ATTENDANCE_FILE, "r") as f:
        return json.load(f)

def save_attendance(attendance):
    with open(ATTENDANCE_FILE, "w") as f:
        json.dump(attendance, f, indent=4)

# --- Attendance page ---
@app.route("/", methods=["GET", "POST"])
def home():
    message = ""
    if request.method == "POST":
        uid = request.form.get("uid").strip()
        students = load_students()
        student = next((s for s in students if s["UID"] == uid), None)
        if student:
            now = datetime.now()
            date_str = str(now.date())
            time_str = str(now.time().replace(microsecond=0))
            attendance = load_attendance()

            if any(a["EnrollmentNo"] == student["EnrollmentNo"] and a["date"] == date_str for a in attendance):
                message = f"⚠️ Attendance already marked for {student['Name']} today."
            else:
                attendance.append({
                    "EnrollmentNo": student["EnrollmentNo"],
                    "Name": student["Name"],
                    "date": date_str,
                    "time": time_str,
                    "status": "Present"
                })
                save_attendance(attendance)
                message = f"✅ Attendance marked for {student['Name']} at {time_str}."
        else:
            message = f"❌ Unknown UID: {uid}"

    return render_template("index.html", message=message)

# --- Student management page ---
@app.route("/manage", methods=["GET", "POST"])
def manage():
    students = load_students()
    if request.method == "POST":
        action = request.form.get("action")
        uid = request.form.get("uid").strip()
        enrollment = request.form.get("enrollment").strip()
        name = request.form.get("name").strip()

        if action == "Add":
            if any(s["UID"] == uid for s in students):
                pass  # UID exists
            else:
                students.append({"UID": uid, "EnrollmentNo": enrollment, "Name": name})
                save_students(students)
        elif action == "Delete":
            students = [s for s in students if s["UID"] != uid]
            save_students(students)

        return redirect(url_for("manage"))

    return render_template("manage.html", students=students)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
