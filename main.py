from fastapi import FastAPI
from sqlmodel import SQLModel, Field, create_engine, Session

# Define the MemoryEntry model
class MemoryEntry(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    content: str

# Connect to the SQLite database
DATABASE_URL = "sqlite:///./test.db"  # Change this URL if using a different database
engine = create_engine(DATABASE_URL, echo=True)

# Create the tables if they don't exist
SQLModel.metadata.create_all(engine)

# Initialize the FastAPI app
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Your FastAPI app is live!"}

@app.post("/memory")
def create_memory_entry(memory_entry: MemoryEntry):
    # Create a new MemoryEntry in the database
    with Session(engine) as session:
        session.add(memory_entry)
        session.commit()
        session.refresh(memory_entry)
    return memory_entry
