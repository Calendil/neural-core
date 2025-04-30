from fastapi import FastAPI, HTTPException, Path, Body, Request
from pydantic import BaseModel
import sqlite3
import os
from functional_notion_api import push_to_notion, fetch_blocks_from_notion

# Initialize the FastAPI app
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Bridge API is live."}

@app.get("/list-files")
def list_files():
    files = os.listdir(".")
    return {"files": files}

# --- 🔒 Isolated: Raw SQL execution ---
"""
from fastapi import Body
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
        with sqlite3.connect("memory-core.db") as conn:
            cursor = conn.cursor()
            cursor.executescript(sql)
            conn.commit()
            return {"result": "SQL executed successfully."}
    except sqlite3.Error as e:
        return {"error": f"SQLite error: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}
"""

# --- 🔒 Isolated: Unfinished memory DB routes ---
"""
from fastapi import HTTPException, Path
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional

class MemoryEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str

class MemoryUpdate(SQLModel):
    title: Optional[str] = None
    content: Optional[str] = None

DATABASE_URL = "sqlite:///./memory-core.db"
engine = create_engine(DATABASE_URL, echo=True)
SQLModel.metadata.create_all(engine)

@app.post("/memory")
def create_memory_entry(memory_entry: MemoryEntry):
    with Session(engine) as session:
        session.add(memory_entry)
        session.commit()
        session.refresh(memory_entry)
    return memory_entry

@app.get("/memory")
def get_memories():
    with Session(engine) as session:
        memories = session.exec(select(MemoryEntry)).all()
    return {"memories": memories}

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
"""

# --- ✅ Active: Notion sync endpoint ---

class NotionSyncRequest(BaseModel):
    page_id: str
    content: str

@app.post("/bridge/notion-sync")
def notion_sync(request: NotionSyncRequest):
    result = push_to_notion(request.page_id, request.content)
    return result

# --- ✅ Active: Notion fetch endpoint ---

@app.get("/bridge/notion-fetch")
def notion_fetch(page_id: str):
    result = fetch_blocks_from_notion(page_id)
    return result
