from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3

app = Flask(__name__)

# Use a writable path when running on serverless platforms like Vercel
def get_database_path() -> str:
    writable_dir = os.environ.get('DB_DIR', '/tmp')
    return os.path.join(writable_dir, 'todo.db')

# Database setup function
def init_db():
    db_path = get_database_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT NOT NULL,
        is_done INTEGER DEFAULT 0
    )
    ''')
    conn.commit()
    conn.close()

# Home page: List tasks
@app.route('/')
def index():
    conn = sqlite3.connect(get_database_path())
    c = conn.cursor()
    c.execute('SELECT * FROM tasks')
    tasks = c.fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

# Add task
@app.route('/add', methods=['POST'])
def add_task():
    task = request.form['task']
    if task:
        conn = sqlite3.connect(get_database_path())
        c = conn.cursor()
        c.execute('INSERT INTO tasks (task) VALUES (?)', (task,))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

# Delete task
@app.route('/delete/<int:id>', methods=['GET'])
def delete_task(id):
    conn = sqlite3.connect(get_database_path())
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Update task (update name)
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_task(id):
    conn = sqlite3.connect(get_database_path())
    c = conn.cursor()
    
    if request.method == 'POST':
        updated_task = request.form['task']
        c.execute('UPDATE tasks SET task = ? WHERE id = ?', (updated_task, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    c.execute('SELECT task FROM tasks WHERE id = ?', (id,))
    task = c.fetchone()
    conn.close()
    
    return render_template('update_task.html', task=task, id=id)

# Mark task as done
@app.route('/done/<int:id>', methods=['POST'])
def mark_done(id):
    conn = sqlite3.connect(get_database_path())
    c = conn.cursor()
    c.execute('UPDATE tasks SET is_done = 1 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Mark task as not done
@app.route('/undone/<int:id>', methods=['POST'])
def mark_undone(id):
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute('UPDATE tasks SET is_done = 0 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Initialize database on import (safe to run repeatedly)
init_db()

if __name__ == '__main__':
    app.run(debug=True)
