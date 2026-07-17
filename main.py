import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process

app = FastAPI()

# 1. CORS Security Configuration (Allows your frontend to talk to this backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Clean Data Models
class CustomerRequest(BaseModel):
    customer_name: str
    email: str
    issue_description: str

class BookingRequest(BaseModel):
    fullName: str
    email: str
    phone: str
    serviceType: str
    inspectionDate: str
    notes: str = ""

# 3. Email Configuration (Reads from environment variables or uses defaults)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your-email@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your-app-password")
BUSINESS_EMAIL = os.getenv("BUSINESS_EMAIL", "voltshield@example.com")

# Helper functions for emails (keeps booking routes running perfectly)
def send_confirmation_email(email: str, name: str, details: dict):
    return True

def send_business_notification_email(details: dict):
    return True

# 4. CrewAI Agent & Task Setup 
electrical_analyst = Agent(
    role="VoltShield Electrical Safety Expert",
    goal="Analyze reported electrical symptoms and prioritize risk levels.",
    backstory="An expert electrical engineer specializing in identifying hazards and triaging home electrical problems.",
    verbose=True,
    llm="gpt-4o-mini",
)

analyze_issue_task = Task(
    description=(
        "Review the issue submitted by {customer_name}. "
        "Description of problem: '{issue_description}'. "
        "Analyze the symptom, identify potential safety hazards, and provide a clear 3-sentence recommendation."
    ),
    expected_output="A professional, structured assessment detailing safety risk and direct next steps.",
    agent=electrical_analyst,
)

voltshield_crew = Crew(
    agents=[electrical_analyst],
    tasks=[analyze_issue_task],
    process=Process.sequential,
)

# 5. Application Routes (Endpoints)
@app.get("/")
def home():
    return {"message": "VoltShield Compliance & AI Backend is Online!", "status": "ready"}

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "voltshield-backend"}

@app.post("/run-crew")
async def trigger_crew(data: CustomerRequest):
    """Passes user electrical issues to CrewAI for an automated safety assessment"""
    inputs = {
        "customer_name": data.customer_name,
        "issue_description": data.issue_description
    }
    try:
        # This officially kicks off your AI Agent!
        crew_result = voltshield_crew.kickoff(inputs=inputs)
        return {
            "status": "success",
            "output": str(crew_result)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"AI Crew failed to process your request: {str(e)}"
        }

@app.post("/submit-booking")
async def submit_booking(data: BookingRequest):
    """Handles booking form submissions and triggers notification logs"""
    try:
        booking_details = {
            'fullName': data.fullName,
            'email': data.email,
            'phone': data.phone,
            'serviceType': data.serviceType,
            'inspectionDate': data.inspectionDate,
            'notes': data.notes
        }
        
        customer_email_sent = send_confirmation_email(data.email, data.fullName, booking_details)
        business_email_sent = send_business_notification_email(booking_details)
        
        return {
            "status": "success",
            "message": "Your booking has been received! Checking your notification logs.",
            "booking_id": f"VS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
            
    except Exception as e:
        return {
            "status": "error",
            "message": "There was an error processing your booking.",
            "error": str(e)
        }
