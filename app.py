
from flask import Flask, render_template, request, redirect, session, flash, url_for
from database import Session, engine, Base
from models import Student, Faculty, Attendance
from attendance_service import AttendanceService
from deepface import DeepFace
import cv2
import os
from werkzeug.utils import secure_filename
import tensorflow as tf 
import mediapipe as mp
import math
import logging

logging.basicConfig(filename='attendance.log', level=locdcdcdzgging.INFO, 
                    format='%(asctime)s - %(message)s')

# =========================
# APP CONFIG
# =========================

app = Flask(__name__)
app.secret_key = "secret_key"

# Create DB tables
Base.metadata.create_all(engine)
db = Session()

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================
# HOME
# =========================

@app.route("/")
def home():
    return render_template("login.html")

# =========================
# REGISTER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        role = request.form.get("role", "").strip()
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not role or not name or not email or not password:
            flash("Error: All fields are required.", "error")
            return redirect("/register")

        if len(password) < 6:
            flash("Error: Password must be at least 6 characters.", "error")
            return redirect("/register")

        if role == "student":

            image = request.files.get("image")
            if not image or not image.filename:
                flash("Error: Please upload an image file.", "error")
                return redirect("/register")

            filename = secure_filename(image.filename)
            ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
            if ext not in {'png', 'jpg', 'jpeg'}:
                flash("Error: Invalid image format. Use PNG or JPG.", "error")
                return redirect("/register")

            path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(path)

            subject = request.form.get("subject", "").strip()
            subject_code = request.form.get("subject_code", "").strip()

            if not subject or not subject_code:
                flash("Error: Subject and Subject Code are required for students.", "error")
                return redirect("/register")

            user = Student(
                name=name,
                email=email,
                password=password,
                image=filename,
                subject=subject,
                subject_code=subject_code
            )

        else:
            user = Faculty(
                name=name,
                email=email,
                password=password
            )

        try:
            db.add(user)
            db.commit()
            flash("Registration successful! Please login.", "success")
            return redirect("/")
        except Exception as e:
            db.rollback()
            flash("Registration error: Email may already exist.", "error")
            return redirect("/register")

    return render_template("register.html")

# =========================
# LOGIN
# =========================

@app.route("/login", methods=["POST"])
def login():

    role = request.form.get("role", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not role or not email or not password:
        flash("Error: All fields are required.", "error")
        return redirect("/")

    if role == "student":

        user = db.query(Student).filter_by(
            email=email, password=password).first()

        if user:
            session["student_id"] = user.id
            flash("Welcome back!", "success")
            return redirect("/student_dashboard")

    else:

        user = db.query(Faculty).filter_by(
            email=email, password=password).first()

        if user:
            session["faculty_id"] = user.id
            flash("Welcome back, Faculty!", "success")
            return redirect("/faculty_dashboard")

    flash("Invalid Email or Password", "error")
    return redirect("/")

# =========================
# STUDENT DASHBOARD
# =========================

@app.route("/student_dashboard")
def student_dashboard():

    if "student_id" not in session:
        return redirect("/")

    attendance = db.query(Attendance).filter_by(
        student_id=session["student_id"]).all()

    return render_template(
        "student_dashboard.html",
        attendance=attendance
    )

# =========================
# FACULTY DASHBOARD
# =========================

@app.route("/faculty_dashboard")
def faculty_dashboard():

    if "faculty_id" not in session:
        return redirect("/")

    students = db.query(Student).all()

    for student in students:
        records = db.query(Attendance).filter_by(student_id=student.id).all()

        total = len(records)
        present = sum(1 for r in records if r.status == "Present")

        student.total_classes = total
        student.present_count = present

    return render_template(
        "faculty_dashboard.html",
        students=students
    )

# =========================
# AI ATTENDANCE (DeepFace)
# =========================

def calculate_ear(landmarks, width, height):
    def dist(p1, p2):
        return math.hypot((p1.x - p2.x)*width, (p1.y - p2.y)*height)

    left_v1 = dist(landmarks[385], landmarks[373])
    left_v2 = dist(landmarks[387], landmarks[380])
    left_h = dist(landmarks[362], landmarks[263])
    left_ear = (left_v1 + left_v2) / (2.0 * left_h) if left_h > 0 else 0

    right_v1 = dist(landmarks[160], landmarks[153])
    right_v2 = dist(landmarks[158], landmarks[144])
    right_h = dist(landmarks[33], landmarks[133])
    right_ear = (right_v1 + right_v2) / (2.0 * right_h) if right_h > 0 else 0

    return (left_ear + right_ear) / 2.0

@app.route("/start_attendance", methods=["POST"])
def start_attendance():
    if "faculty_id" not in session:
        return redirect("/")

    subject = request.form.get("subject", "").strip()
    if not subject:
        flash("Error: Subject is required to start attendance.", "error")
        return redirect("/faculty_dashboard")

    students = db.query(Student).all()
    detected_students = []

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        flash("Camera not working. Check permissions.", "error")
        return redirect("/faculty_dashboard")

    logging.info(f"Camera opened for attendance. Subject: {subject}, Faculty ID: {session['faculty_id']}")
    print("Starting AI Attendance... Press ESC to stop")

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

    EAR_THRESHOLD = 0.22
    CONSECUTIVE_FRAMES = 2
    blink_counter = 0

    while True:
        ret, frame = cam.read()
        if not ret:
            continue

        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        blink_detected_this_frame = False

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                ear = calculate_ear(face_landmarks.landmark, w, h)
                
                if ear < EAR_THRESHOLD:
                    blink_counter += 1
                else:
                    if blink_counter >= CONSECUTIVE_FRAMES:
                        blink_detected_this_frame = True
                    blink_counter = 0

                # Visual feedback for tracking
                cv2.putText(frame, f"EAR: {ear:.2f}", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                if blink_detected_this_frame:
                    cv2.putText(frame, "BLINKED!", (10, 60), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        # Run Heavy Verification ONLY on blink completion
        if blink_detected_this_frame:
            print("Blink detected! Verifying face...")
            for student in students:
                if not student.image: 
                    continue
                image_path = os.path.join(UPLOAD_FOLDER, student.image)
                if not os.path.exists(image_path):
                    continue

                try:
                    res = DeepFace.verify(
                        img1_path=frame,
                        img2_path=image_path,
                        enforce_detection=False,
                        model_name="Facenet",
                        detector_backend="opencv"
                    )

                    if res["verified"] and res["distance"] < 0.5 and student.id not in detected_students:
                        print(f"Matched: {student.name}")
                        detected_students.append(student.id)

                except Exception as e:
                    print("Error:", e)

        # Annotate matched students
        y_offset = 100
        for st in students:
            if st.id in detected_students:
                cv2.putText(frame, f"Present: {st.name}", (50, y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                y_offset += 30

        cv2.imshow("AI Attendance", frame)

        if cv2.waitKey(1) == 27:
            break

    cam.release()
    cv2.destroyAllWindows()
    logging.info("Camera closed.")

    # Remove duplicates just in case
    detected_students = list(set(detected_students))

    # Save attendance
    service = AttendanceService()
    service.mark_attendance(
        db,
        detected_students,
        subject
    )

    flash("Attendance marked successfully!", "success")
    return redirect("/faculty_dashboard")
# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    app.run(debug=True)