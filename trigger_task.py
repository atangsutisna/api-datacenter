from tasks import add, long_running_task

# Call the 'add' task asynchronously
# .delay() is a shortcut for calling a task
result_add = add.delay(4, 4)
print(f"Task 'add' called. Task ID: {result_add.id}")

# Call the 'long_running_task' asynchronously
result_long = long_running_task.delay(10)
print(f"Task 'long_running_task' called. Task ID: {result_long.id}")

print("\nApplication continues immediately, without waiting for the tasks to finish.")

# You can check the status and retrieve results (optional)
# This is a blocking call, only use if you need the result immediately
# In a real-world app, you would check results later or via a different service
print("\nChecking results...")
print(f"Result for 'add' task: {result_add.get(timeout=1)}")
# Note: 'long_running_task' is still running, so this will time out
# print(f"Result for 'long_running_task': {result_long.get()}")
