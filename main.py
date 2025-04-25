from fastapi import FastAPI, HTTPException, Path, Body, Request
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional
import sqlite3

# Define the MemoryEntry model
class MemoryEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str

# Update model for partial updates
class MemoryUpdate(SQLModel):
    title: Optional[str] = None
    content: Optional[str] = None

# Connect to the SQLite database
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=True)
SQLModel.metadata.create_all(engine)

# Initialize the FastAPI app
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Your FastAPI app is live!"}

# Create a memory entry
@app.post("/memory")
def create_memory_entry(memory_entry: MemoryEntry):
    with Session(engine) as session:
        session.add(memory_entry)
        session.commit()
        session.refresh(memory_entry)
    return memory_entry

# Get all memory entries
@app.get("/memory")
def get_memories():
    with Session(engine) as session:
        memories = session.exec(select(MemoryEntry)).all()
    return {"memories": memories}

# Update a memory entry partially
@app.put("/memory/{memory_id}")
def update_memory(memory_id: int = Path(...), memory_update: MemoryUpdate = Body(...)):
    with Session(engine) as session:
        existing_memory = session.get(MemoryEntry, memory_id)
        if not existing_memory:
            raise HTTPException(status_code=404, detail="Memory not found")

        if memory_update.title is not None:
            existing_memory.title = memory_update.title
        if memory_update.content is not None:
            existing_memory.content = memory_update.content

        session.add(existing_memory)
        session.commit()
        session.refresh(existing_memory)
        return {"message": f"Memory with ID {memory_id} updated."}

# Delete a memory entry
@app.delete("/memory/{memory_id}")
def delete_memory(memory_id: int):
    with Session(engine) as session:
        memory_to_delete = session.get(MemoryEntry, memory_id)
        if memory_to_delete:
            session.delete(memory_to_delete)
            session.commit()
            return {"message": f"Memory with ID {memory_id} deleted."}
        else:
            raise HTTPException(status_code=404, detail="Memory not found")

# Execute raw SQL (DDL/DML)
@app.post("/execute-sql")
async def execute_sql(request: Request):
    try:
        body = await request.json()
        sql = body.get("sql")
        if not sql:
            return {"error": "No SQL provided"}
    except Exception as e:
        return {"error": f"Invalid request format: {str(e)}"}

    try:
        with sqlite3.connect("test.db") as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            conn.commit()
            return {"result": result}
    except Exception as e:
        return {"error": str(e)}
