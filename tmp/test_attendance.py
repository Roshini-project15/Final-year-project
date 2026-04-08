from database import Session
from models import Student, Attendance
from attendance_service import AttendanceService
from datetime import datetime

db = Session()
service = AttendanceService()

# 1. Choose a student to test with
student = db.query(Student).first()
if not student:
    print("No students found in DB. Test failed.")
    exit()

print(f"Testing with Student: {student.name}, ID: {student.id}, Subject Code: {student.subject_code}, Subject Name: {student.subject}")

# 2. Mark attendance (once) - Should be Absent if not in detected
service.mark_attendance(db, [], student.subject)
db.expire_all()
records = db.query(Attendance).filter_by(student_id=student.id, date=datetime.now().strftime("%Y-%m-%d")).all()
print(f"Initial run (Absent): Result {len(records)} records. Status: {[r.status for r in records]}")

# 3. Mark attendance again (same day, same subject) - Should OVERWRITE to Present
service.mark_attendance(db, [student.id], student.subject)
db.expire_all()
records = db.query(Attendance).filter_by(student_id=student.id, date=datetime.now().strftime("%Y-%m-%d")).all()
print(f"Second run (overwrite to Present): Result {len(records)} records. Status: {[r.status for r in records]}")

# 4. Final check: There should only be 1 record for this student/date/subject_code
if len(records) == 1 and records[0].status == "Present":
    print("SUCCESS: Attendance logic is working correctly (overwrite + no duplicates).")
else:
    print("FAILURE: Logic error detected.")

db.close()
