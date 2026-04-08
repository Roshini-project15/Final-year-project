from datetime import datetime
from models import Attendance, Student
from sqlalchemy import or_

class AttendanceService:

    def mark_attendance(self, db, detected_student_ids, class_name, subject_name, faculty_id):
        """
        Marks attendance for a specific CLASS and SUBJECT by a specific FACULTY.
        Allows 8+ subjects per day by using different subject names.
        """
        date = datetime.now().strftime("%Y-%m-%d")

        # 1. Get all students registered in this CLASS (e.g., "10th Grade")
        all_students = db.query(Student).filter_by(class_name=class_name).all()

        if not all_students:
            print(f"  [WARN] No students found in class: {class_name}")
            return

        for student in all_students:
            # 2. Check for existing record for THIS SUBJECT and THIS DAY
            existing = db.query(Attendance).filter_by(
                student_id=student.id,
                subject_name=subject_name,
                date=date
            ).first()

            # Decide status: Present if detected, else Absent
            status = "Present" if student.id in detected_student_ids else "Absent"

            if existing:
                # If already marked 'Present', keep it. 
                # Only update if they were 'Absent' but are now detected as 'Present'.
                if existing.status != "Present" and status == "Present":
                    existing.status = "Present"
                    existing.faculty_id = faculty_id
            else:
                # NEW record
                record = Attendance(
                    student_id=student.id,
                    faculty_id=faculty_id,
                    subject_name=subject_name,
                    date=date,
                    status=status
                )
                db.add(record)

        db.commit()