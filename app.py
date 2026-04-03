# app.py

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# -------------------------------
# Database Configuration
# -------------------------------
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL environment variable not set! Cannot connect to PostgreSQL.")

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -------------------------------
# Database Model
# -------------------------------
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    status = db.Column(db.String(20), default="Pending")

    def __repr__(self):
        return f"<Task {self.title}>"

# -------------------------------
# Routes
# -------------------------------
@app.route("/")
def index():
    tasks = Task.query.all()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        task = Task(title=title, description=description)
        db.session.add(task)
        db.session.commit()
        return redirect("/")
    return render_template("add_task.html")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    task = Task.query.get_or_404(id)
    if request.method == "POST":
        task.title = request.form["title"]
        task.description = request.form["description"]
        task.status = request.form.get("status", "Pending")
        db.session.commit()
        return redirect("/")
    return render_template("edit_task.html", task=task)

@app.route("/delete/<int:id>")
def delete(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect("/")

@app.route("/test-db")
def test_db():
    try:
        tasks = Task.query.all()
        return f"Database connected successfully! Tasks count: {len(tasks)}"
    except Exception as e:
        return f"Database connection error: {e}"

# -------------------------------
# Run App
# -------------------------------
with app.app_context():
    db.create_all()  # Ensure tables are created