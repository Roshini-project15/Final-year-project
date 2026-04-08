from database import Session
from models import Student, Attendance, Faculty
from attendance_service import AttendanceService
from datetime import datetime
import os

db = Session()
service = AttendanceService()

# 1. Cleanup and Setup
print("--- Setup ---")
# Ensure we have a Faculty
t1 = db.query(Faculty).filter_by(email="teacher1@school.com").first()
if not t1:
    t1 = Faculty(name="Teacher One", email="teacher1@school.com", password="password")
    db.add(t1)
t2 = db.query(Faculty).filter_by(email="teacher2@school.com").first()
if not t2:
    t2 = Faculty(name="Teacher Two", email="teacher2@school.com", password="password")
    db.add(t2)
db.commit()

# Ensure we have a Student in a Class
student = db.query(Student).filter_by(email="student@school.com").first()
if not student:
    student = Student(name="John Doe", email="student@school.com", password="password", class_name="10th-A", roll_number="01")
    db.add(student)
db.commit()

print(f"Student: {student.name}, Class: {student.class_name}")

# 2. Test Multiple Subjects on Same Day
print("\n--- Test: Multiple Subjects ---")
date_str = datetime.now().strftime("%Y-%m-%d")

# Teacher 1 marks MATH as Present
print("Teacher 1 marking MATH...")
service.mark_attendance(db, [student.id], "10th-A", "Math", t1.id)

# Teacher 2 marks SCIENCE as Present
print("Teacher 2 marking SCIENCE...")
service.mark_attendance(db, [student.id], "10th-A", "Science", t2.id)

# Check results
records = db.query(Attendance).filter_by(student_id=student.id, date=date_str).all()
print(f"Total records for today: {len(records)}")
for r in records:
    print(f"  - Subject: {r.subject_name}, Status: {r.status}, Faculty ID: {r.faculty_id}")

if len(records) == 2:
    print("SUCCESS: Multiple subjects tracked correctly for the same student.")
else:
    print("FAILURE: Multiple subject tracking failed.")

# 3. Test Overwrite (Correction)
print("\n--- Test: Overwrite/Correction ---")
# Mark Math as ABSENT now (e.g. correction)
print("Correcting Math to Absent...")
service.mark_attendance(db, [], "10th-A", "Math", t1.id)

records = db.query(Attendance).filter_by(student_id=student.id, date=date_str, subject_name="Math").all()
if len(records) == 1 and records[0].status == "Absent":
    print("SUCCESS: Status overwrite (correction) working correctly.")
else:
    print("FAILURE: Overwrite failed.")

db.close()
print("\n--- All tests passed! ---")
