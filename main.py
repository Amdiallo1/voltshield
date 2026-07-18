from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class CustomerRequest(BaseModel):
    customer_name: str
    email: str
    issue_description: str

@app.post("/run-crew")
def run_crew(request: CustomerRequest):
    print("DEBUG: Entered the synchronous function!")
    try:
        # We will add your CrewAI logic back in once we confirm this works
        print(f"Processing request for: {request.customer_name}")
        return {"status": "success", "message": "Task processed successfully"}
    except Exception as e:
        print(f"CRASH ERROR: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/")
def read_root():
    return {"status": "online", "message": "VoltShield is active."}
