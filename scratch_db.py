import sqlite3
conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()
cursor.execute("SELECT id, name, email, subject, subject_code FROM students")
rows = cursor.fetchall()
print("| ID | Name | Email | Subject | Code |")
print("|---|---|---|---|---|")
for r in rows:
    print(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} |")
