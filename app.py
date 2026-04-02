# app.py

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Get DATABASE_URL from environment, replace postgres:// -> postgresql:// if needed
database_url = os.environ.get('DATABASE_URL')
if database_url:
    database_url = database_url.replace("postgres://", "postgresql://")

# Configure Flask SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------------------
# Database Model
# -------------------------------
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Pending')

    def __repr__(self):
        return f"<Task {self.title}>"

# -------------------------------
# Routes
# -------------------------------

# Home / list tasks
@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

# Add new task
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        task = Task(title=title, description=description)
        db.session.add(task)
        db.session.commit()
        return redirect('/')
    return render_template('add_task.html')

# Edit task
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    task = Task.query.get_or_404(id)
    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        task.status = request.form.get('status', 'Pending')
        db.session.commit()
        return redirect('/')
    return render_template('edit_task.html', task=task)

# Delete task
@app.route('/delete/<int:id>')
def delete(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect('/')

# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure tables are created
app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))