import asyncio
import smtplib
from email.mime.text import MIMEText
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crewai import Agent, Task, Crew

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="VoltShield API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CustomerRequest(BaseModel):
    customer_name: str
    email: str
    issue_description: str

# --- UPDATED: Email notification function using Resend ---
def send_owner_email(request: CustomerRequest):
    owner_email = os.environ.get("OWNER_EMAIL", "amdiallo1@yandex.com")
    
    email_content = (
        f"========================================\n"
        f"    VOLTSHIELD COMPLIANCE INSPECTION\n"
        f"========================================\n\n"
        f"A new inspection request has been submitted for a commercial or multi-family property.\n\n"
        f"• Customer Name: {request.customer_name}\n"
        f"• Customer Email: {request.email}\n\n"
        f"Issue Description / Safety Details:\n"
        f"{request.issue_description}\n\n"
        f"----------------------------------------\n"
        f"CrewAI analysis is processing in the background."
    )

    params = {
        "from": "VoltShield <onboarding@resend.dev>",
        "to": [owner_email],
        "subject": f"New VoltShield Request from {request.customer_name}",
        "text": email_content,
    }
    resend.Emails.send(params)  # <--- MAKE SURE THIS LINE IS HERE
   
# 1. This route keeps Render happy (fixes the 404 health check)
@app.get("/")
def read_root():
    return {"status": "online", "message": "VoltShield API is ready for tasks."}

# 2. This route handles the AI analysis and email notification directly
@app.post("/run-crew")
async def run_crew_endpoint(request: CustomerRequest):
    try:
        # --- ADDED: Send email notification in background thread ---
        await asyncio.to_thread(send_owner_email, request)

        # Setup the Agent
        analyst = Agent(
            role="Expert Electrician",
            goal="Provide safety and scope analysis",
            backstory="Expert with 30 years experience",
            llm="gpt-4o-mini"
        )

        # Setup the Task
        task = Task(
            description=f"Issue from {request.customer_name}: {request.issue_description}",
            expected_output="Safety hazards, project scale, and next steps.",
            agent=analyst
        )

        # Execute
        crew = Crew(agents=[analyst], tasks=[task])
        result = await crew.akickoff()
        
        # Return result to user
        return {
            "status": "success", 
            "customer": request.customer_name,
            "analysis": str(result)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
