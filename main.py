import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crewai import Agent, Task, Crew

# Initialize FastAPI application
app = FastAPI(
    title="VoltShield Compliance & AI Backend",
    version="1.0.0"
)

# Enable CORS so your frontend application can communicate with this backend smoothly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to specific URLs in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------
# Pydantic Schemas (Matches your verified openapi.json structure)
# ---------------------------------------------------------------------
class CustomerRequest(BaseModel):
    customer_name: str
    email: str
    issue_description: str


# ---------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------

@app.get("/")
def read_root():
    """Root health check endpoint to verify backend status."""
    return {
        "message": "VoltShield Compliance & AI Backend is Online!",
        "status": "ready"
    }


@app.post("/run-crew")
def run_crew(request: CustomerRequest):
    """
    Triggers the CrewAI agent group to analyze the electrical issue.
    Note: 'async' is intentionally omitted here to prevent CrewAI 
    from clashing with FastAPI's asynchronous event loop.
    """
    try:
        # 1. Define the Electrical Expert Agent
        analyst = Agent(
            role="Senior Electrical Triage Expert",
            goal="Analyze customer requests to determine project scope, required materials, and safety priorities.",
            backstory="You are an expert electrician with decades of field experience. You look at client descriptions, identify core hazards (like exposed wiring or overload signs), and outline technical requirements.",
            verbose=True,  # Set to True so you can monitor agent thinking in Render logs
            memory=False
        )
        
        # 2. Define the specific analysis task
        analysis_task = Task(
            description=(
                f"Analyze the following electrical issue submitted by {request.customer_name} ({request.email}):\n"
                f"\"{request.issue_description}\"\n\n"
                "Identify potential safety hazards, project scale, and initial troubleshooting steps or technical requirements."
            ),
            expected_output="A detailed summary outlining safety concerns, estimated project type, and material recommendations.",
            agent=analyst
        )
        
        # 3. Assemble the Crew
        crew = Crew(
            agents=[analyst],
            tasks=[analysis_task],
            verbose=True
        )
        
        # 4. Kick off processing synchronously in a dedicated thread worker pool
        result = crew.kickoff()
        
        # 5. Return clean structured JSON response back to client
        return {
            "status": "success",
            "message": str(result)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"AI Crew failed to process your request: {str(e)}"
        }
