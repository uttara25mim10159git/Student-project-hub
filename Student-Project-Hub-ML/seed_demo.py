from app import get_db, init_db
from werkzeug.security import generate_password_hash

init_db()
conn = get_db()
conn.execute("INSERT OR IGNORE INTO students(name,email,password,branch,year,skills) VALUES(?,?,?,?,?,?)",
             ("Demo Student","demo@student.local",generate_password_hash("demo123"),"AI/ML",2,"Python, Machine Learning, Flask"))
student = conn.execute("SELECT id FROM students WHERE email=?",("demo@student.local",)).fetchone()
if student:
    exists = conn.execute("SELECT id FROM projects WHERE title=?",("Campus FAQ Chatbot",)).fetchone()
    if not exists:
        conn.execute("""INSERT INTO projects(title,description,domain,technologies,difficulty,team_size,status,owner_id)
                        VALUES(?,?,?,?,?,?,?,?)""",
                     ("Campus FAQ Chatbot","A small chatbot that answers common college-related questions from a prepared FAQ dataset.",
                      "AI/ML","Python, NLP, Flask","Intermediate",2,"Completed",student["id"]))
conn.commit()
conn.close()
print("Demo data created. Login: demo@student.local / demo123")
