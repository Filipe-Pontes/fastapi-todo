from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os
from contextlib import contextmanager

app = FastAPI(title="ToDo API with FastAPI")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "tasks")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "321976548")
DB_PORT = os.getenv("DB_PORT", "5433")

class Task(BaseModel):
    task: str

@contextmanager
def get_db_cursor():
    conn = psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS, port=int(DB_PORT)
    )
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    finally:
        cur.close()
        conn.close()

# Cria a tabela uma única vez
with get_db_cursor() as cur:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            task TEXT NOT NULL
        );
    """)

@app.get("/tasks")
def get_tasks():
    with get_db_cursor() as cur:
        cur.execute("SELECT id, task FROM tasks;")
        tasks = [{"id": t[0], "task": t[1]} for t in cur.fetchall()]
    return tasks

@app.post("/tasks")
def create_task(task: Task):
    with get_db_cursor() as cur:
        cur.execute("INSERT INTO tasks (task) VALUES (%s) RETURNING id;", (task.task,))
        task_id = cur.fetchone()[0]
    return {"id": task_id, "task": task.task}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    with get_db_cursor() as cur:
        cur.execute("DELETE FROM tasks WHERE id = %s RETURNING id;", (task_id,))
        deleted = cur.fetchone()
    if deleted is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return {"message": f"Tarefa {task_id} deletada com sucesso"}
