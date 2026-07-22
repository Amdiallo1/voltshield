import asyncio
import smtplib
from email.mime.text import MIMEText
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crewai import Agent, Task, Crew

app = FastAPI(title="VoltShield API")

class CustomerRequest(BaseModel):
    customer_name: str
    email: str
    issue_description: str

# --- ADDED: Email notification function ---
def send_owner_email(request: CustomerRequest):
    sender_email = "your-email@yandex.com"
    app_password = "your-yandex-app-password"  # Your Yandex App Password
    owner_email = "your-email@yandex.com"

    msg = MIMEText(
        f"========================================\n"
        f"   VOLTSHIELD COMPLIANCE INSPECTION\n"
        f"========================================\n\n"
        f"A new inspection request has been submitted for a commercial or multi-family property.\n\n"
        f"• Customer Name: {request.customer_name}\n"
        f"• Customer Email: {request.email}\n\n"
        f"Issue Description / Safety Details:\n"
        f"{request.issue_description}\n\n"
        f"----------------------------------------\n"
        f"CrewAI analysis is processing in the background."
    )
    msg["Subject"] = f"[VoltShield Compliance] Inspection Request: {request.customer_name}"
    msg["From"] = sender_email
    msg["To"] = owner_email

    with smtplib.SMTP_SSL("smtp.yandex.com", 465) as server:
        server.login(sender_email, app_password)
        server.sendmail(sender_email, owner_email, msg.as_string())

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
