from fastapi import FastAPI
from sqlmodel import SQLModel, Field, create_engine, Session

app = FastAPI()

engine = create_engine("sqlite:///memory.db")

class Memory(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content: str

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get("/")
def read_root():
    return {"message": "Your FastAPI app is live!"}

@app.post("/memory")
def create_memory(content: str):
    memory = Memory(content=content)
    with Session(engine) as session:
        session.add(memory)
        session.commit()
        session.refresh(memory)
    return memory
