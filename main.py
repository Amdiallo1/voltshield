import uuid
import json
import os
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
QUEUE_DIR = "task_queue"
os.makedirs(QUEUE_DIR, exist_ok=True)

class CustomerRequest(BaseModel):
    customer_name: str
    email: str
    issue_description: str

@app.post("/run-crew")
async def run_crew(request: CustomerRequest):
    request_id = str(uuid.uuid4())
    # Save request to a JSON file; the worker picks this up
    with open(f"{QUEUE_DIR}/{request_id}.json", "w") as f:
        json.dump(request.dict(), f)
    return {"status": "queued", "request_id": request_id}

@app.get("/")
def read_root():
    return {"status": "online", "message": "VoltShield is active."}
