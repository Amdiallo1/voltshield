from fastapi import FastAPI
from pydantic import BaseModel
from crewai import Agent, Task, Crew

app = FastAPI()

class CustomerRequest(BaseModel):
    customer_name: str
    email: str
    issue_description: str

@app.post("/run-crew")
def run_crew(request: CustomerRequest):
    # Safety: Define result as None first
    result = None
    
    try:
        # Define the AI Agent
        electrician = Agent(
            role="Electrician",
            goal="Provide safety assessment for electrical issues",
            backstory="Expert electrician",
            verbose=True
        )
        
        # Define the Task
        task = Task(
            description=f"Issue reported: {request.issue_description}",
            expected_output="Safety advice",
            agent=electrician
        )
        
        # Run the Crew
        crew = Crew(agents=[electrician], tasks=[task])
        result = crew.kickoff()
        
        # Success response
        return {"status": "success", "result": str(result)}
        
    except Exception as e:
        # If an error happens, return the error message (not 'result')
        return {"status": "error", "message": str(e)}

@app.get("/")
def read_root():
    return {"status": "online"}
