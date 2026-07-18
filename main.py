import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
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

executor = ThreadPoolExecutor(max_workers=3)

def execute_crew(customer_name, email, issue_description):
    # Fallback to check if key exists, defaults to dummy if missing to avoid crash before execution
    if not os.environ.get("OPENAI_API_KEY"):
        return "Error: OPENAI_API_KEY environment variable is not set on Render."

    analyst = Agent(
        role="Senior Electrical Triage Expert",
        goal="Analyze customer requests to determine project scope, required materials, and safety priorities.",
        backstory="You are an expert electrician with decades of field experience. You look at client descriptions, identify core hazards and outline technical requirements.",
        verbose=True,
        memory=False,
        llm="gpt-4o-mini"
    )
    
    analysis_task = Task(
        description=(
            f"Analyze the following electrical issue submitted by {customer_name} ({email}):\n"
            f"\"{issue_description}\"\n\n"
            "Identify potential safety hazards, project scale, and initial troubleshooting steps or technical requirements."
        ),
        expected_output="A detailed summary outlining safety concerns, estimated project type, and material recommendations.",
        agent=analyst
    )
    
    crew = Crew(agents=[analyst], tasks=[analysis_task], verbose=True)
    return crew.kickoff()

@app.get("/")
def read_root():
    return {"message": "VoltShield Compliance & AI Backend is Online!", "status": "ready"}

@app.post("/run-crew")
async def run_crew(request: CustomerRequest):
    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            executor, 
            execute_crew, 
            request.customer_name, 
            request.email, 
            request.issue_description
        )
        return {"status": "success", "message": str(result)}
    except Exception as e:
        return {"status": "error", "message": f"AI Crew failed to process your request: {str(e)}"}
