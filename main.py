# main.py

from fastapi import FastAPI
from functional_memory_db import app as functional_memory_db_app

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Bridge API is live."}

app.mount("/functional-memory-db", functional_memory_db_app)
