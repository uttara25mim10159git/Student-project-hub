from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from ml.recommender import recommend_projects
from ml.classifier import predict_project
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "projecthub.db"

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        branch TEXT NOT NULL,
        year INTEGER NOT NULL,
        skills TEXT DEFAULT ''
    );

    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        domain TEXT NOT NULL,
        technologies TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        team_size INTEGER DEFAULT 1,
        github_link TEXT DEFAULT '',
        demo_link TEXT DEFAULT '',
        status TEXT DEFAULT 'Completed',
        ml_domain TEXT DEFAULT '',
        ml_confidence REAL DEFAULT 0,
        owner_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(owner_id) REFERENCES students(id)
    );

    CREATE TABLE IF NOT EXISTS join_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        message TEXT DEFAULT '',
        status TEXT DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(project_id, student_id),
        FOREIGN KEY(project_id) REFERENCES projects(id),
        FOREIGN KEY(student_id) REFERENCES students(id)
    );
    """)
    # Keep older local databases compatible with the ML fields.
    columns = {row[1] for row in conn.execute("PRAGMA table_info(projects)").fetchall()}
    if "ml_domain" not in columns:
        conn.execute("ALTER TABLE projects ADD COLUMN ml_domain TEXT DEFAULT ''")
    if "ml_confidence" not in columns:
        conn.execute("ALTER TABLE projects ADD COLUMN ml_confidence REAL DEFAULT 0")
    conn.commit()
    conn.close()

@app.context_processor
def inject_user():
    return {"current_user": session.get("user")}

@app.route("/")
def index():
    conn = get_db()
    projects = conn.execute("""
        SELECT p.*, s.name AS owner_name
        FROM projects p JOIN students s ON p.owner_id=s.id
        ORDER BY p.created_at DESC
        LIMIT 6
    """).fetchall()
    conn.close()
    return render_template("index.html", projects=projects)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        branch = request.form["branch"].strip()
        year = request.form["year"]

        if not all([name, email, password, branch, year]):
            flash("Please fill all required fields.", "error")
            return redirect(url_for("register"))

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO students(name,email,password,branch,year) VALUES(?,?,?,?,?)",
                (name, email, generate_password_hash(password), branch, int(year))
            )
            conn.commit()
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("An account with this email already exists.", "error")
        finally:
            conn.close()
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        conn = get_db()
        student = conn.execute("SELECT * FROM students WHERE email=?", (email,)).fetchone()
        conn.close()
        if student and check_password_hash(student["password"], password):
            session["user"] = {
                "id": student["id"], "name": student["name"],
                "email": student["email"], "branch": student["branch"],
                "year": student["year"], "skills": student["skills"]
            }
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    uid = session["user"]["id"]
    conn = get_db()
    my_projects = conn.execute(
        "SELECT * FROM projects WHERE owner_id=? ORDER BY created_at DESC", (uid,)
    ).fetchall()
    requests = conn.execute("""
        SELECT jr.*, p.title, s.name AS student_name, s.email
        FROM join_requests jr
        JOIN projects p ON jr.project_id=p.id
        JOIN students s ON jr.student_id=s.id
        WHERE p.owner_id=?
        ORDER BY jr.created_at DESC
    """, (uid,)).fetchall()
    conn.close()
    return render_template("dashboard.html", projects=my_projects, requests=requests)

@app.route("/projects")
def projects():
    q = request.args.get("q", "").strip()
    domain = request.args.get("domain", "").strip()
    difficulty = request.args.get("difficulty", "").strip()

    sql = """SELECT p.*, s.name AS owner_name FROM projects p
             JOIN students s ON p.owner_id=s.id WHERE 1=1"""
    params = []
    if q:
        sql += " AND (p.title LIKE ? OR p.description LIKE ? OR p.technologies LIKE ?)"
        like = f"%{q}%"
        params.extend([like, like, like])
    if domain:
        sql += " AND p.domain=?"
        params.append(domain)
    if difficulty:
        sql += " AND p.difficulty=?"
        params.append(difficulty)
    sql += " ORDER BY p.created_at DESC"

    conn = get_db()
    project_rows = conn.execute(sql, params).fetchall()
    domains = [r["domain"] for r in conn.execute("SELECT DISTINCT domain FROM projects ORDER BY domain")]
    conn.close()
    return render_template("projects.html", projects=project_rows, domains=domains,
                           q=q, selected_domain=domain, selected_difficulty=difficulty)

@app.route("/project/new", methods=["GET", "POST"])
def new_project():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        data = [request.form.get(k, "").strip() for k in
                ["title","description","domain","technologies","difficulty","github_link","demo_link","status"]]
        team_size = request.form.get("team_size", "1")
        if not all(data[:5]):
            flash("Please complete the required project fields.", "error")
            return render_template("project_form.html", project=None)
        ml_text = f"{data[0]} {data[1]} {data[3]}"
        predicted_domain, confidence = predict_project(ml_text)
        conn = get_db()
        conn.execute("""INSERT INTO projects
            (title,description,domain,technologies,difficulty,team_size,github_link,demo_link,status,ml_domain,ml_confidence,owner_id)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
            (data[0],data[1],data[2],data[3],data[4],int(team_size or 1),
             data[5],data[6],data[7] or "Completed",predicted_domain,confidence,session["user"]["id"]))
        conn.commit()
        conn.close()
        flash(f"Project added successfully. ML classified it as {predicted_domain} ({confidence:.0%} confidence).", "success")
        return redirect(url_for("dashboard"))
    return render_template("project_form.html", project=None)

@app.route("/project/<int:project_id>")
def project_detail(project_id):
    conn = get_db()
    project = conn.execute("""SELECT p.*, s.name AS owner_name, s.branch, s.year
                              FROM projects p JOIN students s ON p.owner_id=s.id
                              WHERE p.id=?""", (project_id,)).fetchone()
    if not project:
        conn.close()
        return "Project not found", 404
    recommendations = recommend_projects(project, conn, limit=3)
    conn.close()
    return render_template("project_detail.html", project=project, recommendations=recommendations)

@app.route("/project/<int:project_id>/delete", methods=["POST"])
def delete_project(project_id):
    if "user" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    owner = conn.execute("SELECT owner_id FROM projects WHERE id=?", (project_id,)).fetchone()
    if owner and owner["owner_id"] == session["user"]["id"]:
        conn.execute("DELETE FROM join_requests WHERE project_id=?", (project_id,))
        conn.execute("DELETE FROM projects WHERE id=?", (project_id,))
        conn.commit()
        flash("Project deleted.", "success")
    else:
        flash("You can only delete your own projects.", "error")
    conn.close()
    return redirect(url_for("dashboard"))

@app.route("/project/<int:project_id>/join", methods=["POST"])
def join_project(project_id):
    if "user" not in session:
        return redirect(url_for("login"))
    message = request.form.get("message", "").strip()
    conn = get_db()
    try:
        conn.execute("INSERT INTO join_requests(project_id,student_id,message) VALUES(?,?,?)",
                     (project_id, session["user"]["id"], message))
        conn.commit()
        flash("Join request sent.", "success")
    except sqlite3.IntegrityError:
        flash("You have already requested to join this project.", "error")
    conn.close()
    return redirect(url_for("project_detail", project_id=project_id))

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user" not in session:
        return redirect(url_for("login"))
    uid = session["user"]["id"]
    conn = get_db()
    if request.method == "POST":
        skills = request.form.get("skills", "").strip()
        conn.execute("UPDATE students SET skills=? WHERE id=?", (skills, uid))
        conn.commit()
        session["user"]["skills"] = skills
        flash("Profile updated.", "success")
    student = conn.execute("SELECT * FROM students WHERE id=?", (uid,)).fetchone()
    project_count = conn.execute("SELECT COUNT(*) c FROM projects WHERE owner_id=?", (uid,)).fetchone()["c"]
    conn.close()
    return render_template("profile.html", student=student, project_count=project_count)

@app.route("/api/projects")
def api_projects():
    conn = get_db()
    rows = conn.execute("SELECT id,title,domain,difficulty,technologies FROM projects ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
