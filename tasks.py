from celery import Celery

app = Celery("hello", broker='redis://localhost:6379/0')

@app.task
def hello():
    return "hello world"

@app.task
def add(x, y):
    """A simple task to add two numbers."""
    print(f"Executing task 'add' with arguments: {x}, {y}")
    return x + y

@app.task
def long_running_task(duration):
    """Simulates a task that takes a long time."""
    import time
    print(f"Starting long_running_task for {duration} seconds.")
    time.sleep(duration)
    print(f"Finished long_running_task.")
    return f"Task completed after {duration} seconds."