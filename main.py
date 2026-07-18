import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crewai import Agent, Task, Crew

app = FastAPI(title="VoltShield Compliance & AI Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CustomerRequest(BaseModel):
    customer_name: str
    email: str
    issue_description: str

@app.get("/")
def read_root():
    return {"message": "VoltShield Compliance & AI Backend is Online!", "status": "ready"}

@app.post("/run-crew")
def run_crew(request: CustomerRequest):
    try:
        analyst = Agent(
            role="Senior Electrical Triage Expert",
            goal="Analyze customer requests to determine project scope, required materials, and safety priorities.",
            backstory="You are an expert electrician with decades of field experience. You look at client descriptions, identify core hazards (like exposed wiring or overload signs), and outline technical requirements.",
            verbose=True,
            memory=False
        )
        
        analysis_task = Task(
            description=(
                f"Analyze the following electrical issue submitted by {request.customer_name} ({request.email}):\n"
                f"\"{request.issue_description}\"\n\n"
                "Identify potential safety hazards, project scale, and initial troubleshooting steps or technical requirements."
            ),
            expected_output="A detailed summary outlining safety concerns, estimated project type, and material recommendations.",
            agent=analyst
        )
        
        crew = Crew(agents=[analyst], tasks=[analysis_task], verbose=True)
        result = crew.kickoff()
        
        return {"status": "success", "message": str(result)}
        
    except Exception as e:
        return {"status": "error", "message": f"AI Crew failed to process your request: {str(e)}"}
