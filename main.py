from flask import Flask
from src.runner import process_scheduled_tasks
import time

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/scheduled-tasks/run")
def run_tasks():
    start = time.time()
    process_scheduled_tasks()
    spent = time.time() - start
    return f'Processed tasks in {spent} seconds'

if __name__ == '__main__':
    app.run('0.0.0.0', 5000, debug=True)
