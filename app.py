# app.py

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Load environment variables from .env (for local testing)
load_dotenv()

app = Flask(__name__)

# -------------------------------
# Database Configuration
# -------------------------------
# Use Railway DATABASE_URL if available, else fallback to local SQLite
database_url = os.environ.get("DATABASE_URL")

if not database_url:
    print("Warning: DATABASE_URL not set. Using local SQLite database.")
    database_url = "sqlite:///tasks.db"

# SQLAlchemy expects 'postgresql://' instead of 'postgres://'
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

# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure tables are created

    # Railway provides the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False") == "True"
    app.run(debug=debug, host="0.0.0.0", port=port)