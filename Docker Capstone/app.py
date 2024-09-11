from flask import Flask, request, render_template, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  

DATABASE = 'todo.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            done BOOLEAN NOT NULL CHECK (done IN (0, 1))
        )
        ''')
        conn.commit()


@app.route('/')
def index():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

@app.route('/task/new', methods=['GET', 'POST'])
def create_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        done = request.form.get('done', '0') == '1'

        if not title:
            flash('Title is required!')
            return render_template('create_task.html')

        conn = get_db_connection()
        conn.execute('INSERT INTO tasks (title, description, done) VALUES (?, ?, ?)',
                     (title, description, done))
        conn.commit()
        conn.close()
        flash('Task created successfully!')
        return redirect(url_for('index'))

    return render_template('create_task.html')

@app.route('/task/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()

    if task is None:
        flash('Task not found!')
        conn.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        done = request.form.get('done', '0') == '1'

        conn.execute('UPDATE tasks SET title = ?, description = ?, done = ? WHERE id = ?',
                     (title, description, done, task_id))
        conn.commit()
        conn.close()
        flash('Task updated successfully!')
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit_task.html', task=task)

@app.route('/task/delete/<int:task_id>', methods=['GET', 'POST'])
def confirm_delete(task_id):
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()

    if task is None:
        flash('Task not found!')
        conn.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()
        flash('Task deleted successfully!')
        return redirect(url_for('index'))

    conn.close()
    return render_template('confirm_delete.html', task=task)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
