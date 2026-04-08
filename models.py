from sqlalchemy import Column, Integer, String, Date, ForeignKey
from database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    image = Column(String, nullable=True)  # path to photo
    class_name = Column(String, nullable=True)     # Renamed from subject
    roll_number = Column(String, nullable=True)    # Renamed from subject_code


class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculty.id"), nullable=True) # Who marked it
    subject_name = Column(String, nullable=False)    # The subject being marked
    date = Column(String, nullable=False)            # store as YYYY-MM-DD string
    status = Column(String, nullable=False)          # "Present" or "Absent"