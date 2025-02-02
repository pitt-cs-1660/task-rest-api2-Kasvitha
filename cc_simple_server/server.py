from fastapi import FastAPI, HTTPException, status
from cc_simple_server.models import TaskCreate, TaskRead
from cc_simple_server.database import init_db, get_db_connection

# Initialize database
init_db()

# Initialize FastAPI app
app = FastAPI()


@app.get("/")
async def read_root():
    """
    Home route returning a welcome message.
    """
    return {"message": "Welcome to the Cloud Computing!"}


# POST ROUTE - Create a new task (Fixed status code to 200 OK)
@app.post("/tasks/", response_model=TaskRead, status_code=status.HTTP_200_OK)
async def create_task(task_data: TaskCreate):
    """
    Create a new task in the database.

    Args:
        task_data (TaskCreate): The task data to be created.

    Returns:
        TaskRead: The created task with an assigned ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks (title, description, completed) VALUES (?, ?, ?)",
        (task_data.title, task_data.description, task_data.completed),
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()

    return TaskRead(id=task_id, title=task_data.title, description=task_data.description, completed=task_data.completed)


# GET ROUTE - Retrieve all tasks
@app.get("/tasks/", response_model=list[TaskRead])
async def get_tasks():
    """
    Retrieve all tasks from the database.

    Returns:
        list[TaskRead]: A list of all tasks.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    conn.close()

    return [TaskRead(id=task[0], title=task[1], description=task[2], completed=task[3]) for task in tasks]


# PUT ROUTE - Update a task
@app.put("/tasks/{task_id}/", response_model=TaskRead)
async def update_task(task_id: int, task_data: TaskCreate):
    """
    Update an existing task by ID.

    Args:
        task_id (int): The ID of the task to be updated.
        task_data (TaskCreate): The updated task data.

    Returns:
        TaskRead: The updated task details.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if task exists before updating
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    existing_task = cursor.fetchone()

    if not existing_task:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    cursor.execute(
        "UPDATE tasks SET title = ?, description = ?, completed = ? WHERE id = ?",
        (task_data.title, task_data.description, task_data.completed, task_id),
    )
    conn.commit()
    conn.close()

    return TaskRead(id=task_id, title=task_data.title, description=task_data.description, completed=task_data.completed)


# DELETE ROUTE - Delete a task
@app.delete("/tasks/{task_id}/")
async def delete_task(task_id: int):
    """
    Delete a task by ID.

    Args:
        task_id (int): The ID of the task to be deleted.

    Returns:
        dict: Success message if task is deleted.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if task exists before deleting
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    existing_task = cursor.fetchone()

    if not existing_task:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    return {"message": f"Task {task_id} deleted successfully"}
