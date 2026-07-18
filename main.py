from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
# Add your other necessary imports here (e.g., from crewai import Agent, Task, Crew)

app = FastAPI()

# 1. Define your Request Model
class CustomerRequest(BaseModel):
    customer_name: str
    email: str
    issue_description: str

# 2. This is the new function that runs the AI in the background
def run_ai_analysis(customer_name: str, email: str, issue: str):
    print("DEBUG: Entered the background task function!")
    try:
        # --- YOUR AGENT LOGIC HERE ---
        print(f"Starting analysis for {customer_name}...")
        # (Make sure your Agent/Task code is here)
        
    except Exception as e:
        print(f"DEBUG: CRASHED with error: {e}")

# 3. Your new Endpoint
@app.post("/run-crew")
async def run_crew(request: CustomerRequest, background_tasks: BackgroundTasks):
    # This triggers the AI task without waiting for it to finish
    background_tasks.add_task(
        run_ai_analysis, 
        request.customer_name, 
        request.email, 
        request.issue_description
    )
    
    # Send an immediate response back to the user
    return {"status": "processing", "message": "Analysis started in background."}

@app.get("/")
def read_root():
    return {"status": "online", "message": "VoltShield is active."}
