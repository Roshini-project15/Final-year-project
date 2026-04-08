from database import Session, engine, Base
from models import Student, Faculty
import os

# Create tables
Base.metadata.create_all(engine)
db = Session()

UPLOAD_FOLDER = "static/uploads"

# -------------------------
# ADD STUDENTS
# -------------------------

students = [
    {"name": "Ravi", "email": "ravi@gmail.com", "password": "123", "image": "ravi.jpg", "subject": "Math", "code": "M101"},
    {"name": "Asha", "email": "asha@gmail.com", "password": "123", "image": "asha.jpg", "subject": "Science", "code": "S102"},
    {"name": "Rahul", "email": "rahul@gmail.com", "password": "123", "image": "rahul.jpg", "subject": "English", "code": "E103"},
    {"name": "Priya", "email": "priya@gmail.com", "password": "123", "image": "priya.jpg", "subject": "Computer", "code": "C104"},
    {"name": "Kiran", "email": "kiran@gmail.com", "password": "123", "image": "kiran.jpg", "subject": "Physics", "code": "P105"}
]
for s in students:
    existing = db.query(Student).filter_by(email=s["email"]).first()
    if not existing:
        student = Student(
    name=s["name"],
    email=s["email"],
    password=s["password"],
    image=s["image"],
    subject=s["subject"],
    subject_code=s["code"]
)
        db.add(student)

# -------------------------
# ADD FACULTY
# -------------------------

faculty_list = [
    {"name": "Mr. Kumar", "email": "kumar@gmail.com", "password": "123"},
    {"name": "Ms. Devi", "email": "devi@gmail.com", "password": "123"}
]

for f in faculty_list:
    existing = db.query(Faculty).filter_by(email=f["email"]).first()
    if not existing:
        faculty = Faculty(
            name=f["name"],
            email=f["email"],
            password=f["password"]
        )
        db.add(faculty)

db.commit()

print("✅ Dummy data inserted successfully!")