from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session, select

# Define the MemoryEntry model
class MemoryEntry(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    content: str

# Connect to the SQLite database
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=True)
SQLModel.metadata.create_all(engine)  # Ensure tables are created

# Initialize the FastAPI app
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Your FastAPI app is live!"}

# POST request for creating a memory entry
@app.post("/memory")
def create_memory_entry(memory_entry: MemoryEntry):
    with Session(engine) as session:
        session.add(memory_entry)
        session.commit()
        session.refresh(memory_entry)
    return memory_entry

# GET request to retrieve all memory entries
@app.get("/memory")
def get_memories():
    with Session(engine) as session:
        memories = session.exec(select(MemoryEntry)).all()
    return {"memories": [memory.content for memory in memories]}

# PUT request to update an existing memory entry by ID
@app.put("/memory/{memory_id}")
def update_memory(memory_id: int, memory_entry: MemoryEntry):
    with Session(engine) as session:
        existing_memory = session.get(MemoryEntry, memory_id)
        if existing_memory:
            existing_memory.title = memory_entry.title
            existing_memory.content = memory_entry.content
            session.commit()
            session.refresh(existing_memory)
            return {"message": f"Memory with ID {memory_id} updated."}
        else:
            raise HTTPException(status_code=404, detail="Memory not found")

# DELETE request to remove a memory entry by ID
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
