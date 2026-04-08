from werkzeug.security import generate_password_hash, check_password_hash
from app import db, Student, Faculty

def test_registration_flow():
    test_email_fac = "test_faculty@example.com"
    test_email_stu = "test_student@example.com"
    test_password = "password123"

    # Clean up
    for u in db.query(Faculty).filter_by(email=test_email_fac).all():
        db.delete(u)
    for u in db.query(Student).filter_by(email=test_email_stu).all():
        db.delete(u)
    db.commit()

    print("Checking Faculty Registration...")
    hashed_pw_fac = generate_password_hash(test_password)
    fac = Faculty(name="Test Faculty", email=test_email_fac, password=hashed_pw_fac)
    db.add(fac)
    db.commit()
    
    fac_db = db.query(Faculty).filter_by(email=test_email_fac).first()
    if fac_db and check_password_hash(fac_db.password, test_password):
        print("SUCCESS: Faculty registered and login verified.")
    else:
        print("FAILURE: Faculty registration failed.")

    print("Checking Student Registration...")
    hashed_pw_stu = generate_password_hash(test_password)
    stu = Student(
        name="Test Student", email=test_email_stu, password=hashed_pw_stu,
        image="test.jpg", class_name="10A", roll_number="1"
    )
    db.add(stu)
    db.commit()
    
    stu_db = db.query(Student).filter_by(email=test_email_stu).first()
    if stu_db and check_password_hash(stu_db.password, test_password):
        print("SUCCESS: Student registered and login verified.")
    else:
        print("FAILURE: Student registration failed.")

if __name__ == "__main__":
    test_registration_flow()
