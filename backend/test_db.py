from database import get_db, init_db

init_db()

db = get_db()
student = db.execute("SELECT * FROM users WHERE role = 'student' LIMIT 1").fetchone()
if student:
    print('Student found:', dict(student))
    docs = db.execute("SELECT COUNT(*) as cnt FROM student_documents WHERE student_id = %s", (student['id'],)).fetchone()
    print('Documents count:', docs['cnt'])
    types = db.execute("SELECT COUNT(*) as cnt FROM document_types").fetchone()
    print('Document types:', types['cnt'])
else:
    print('No student found')
db.close()
