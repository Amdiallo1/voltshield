import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process, LLM

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

# 3. Yandex Email Configuration (Reads from Render environment variables)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.yandex.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your-email@yandex.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your-app-password")
BUSINESS_EMAIL = os.getenv("BUSINESS_EMAIL", "your-email@yandex.com")

def send_confirmation_email(customer_email: str, customer_name: str, details: dict):
    """Sends a professional HTML confirmation email back to the customer"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "⚡ VoltShield Booking Confirmation"
        msg["From"] = SENDER_EMAIL
        msg["To"] = customer_email

        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; padding: 20px; border-radius: 8px;">
                    <h2 style="color: #0284c7;">Thank You for Booking, {customer_name}!</h2>
                    <p>We have successfully scheduled your electrical assessment request. Our team will review your details shortly.</p>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    <h3>Inspection Details:</h3>
                    <p><strong>Service Requested:</strong> {details['serviceType']}</p>
                    <p><strong>Proposed Date:</strong> {details['inspectionDate']}</p>
                    <p><strong>Notes Provided:</strong> {details['notes'] if details['notes'] else 'None'}</p>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="font-size: 12px; color: #777;">VoltShield Compliance and Safety Systems Inc.</p>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(html, "html"))

        # Secure SSL connection required for Yandex Port 465
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, customer_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[Email Error] Failed to send customer confirmation: {str(e)}")
        return False

def send_business_notification_email(details: dict):
    """Alerts YOUR inbox instantly that a new lead has arrived"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🚨 NEW BOOKING: {details['serviceType']} - {details['fullName']}"
        msg["From"] = SENDER_EMAIL
        msg["To"] = BUSINESS_EMAIL

        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; padding: 20px; border-radius: 8px; background-color: #fcfcfc;">
                    <h2 style="color: #dc2626;">New Sales Lead / Inspection Requested</h2>
                    <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                        <tr><td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Customer Name:</strong></td><td style="padding: 8px 0; border-bottom: 1px solid #eee;">{details['fullName']}</td></tr>
                        <tr><td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Email:</strong></td><td style="padding: 8px 0; border-bottom: 1px solid #eee;">{details['email']}</td></tr>
                        <tr><td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Phone:</strong></td><td style="padding: 8px 0; border-bottom: 1px solid #eee;">{details['phone']}</td></tr>
                        <tr><td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Service Type:</strong></td><td style="padding: 8px 0; border-bottom: 1px solid #eee;">{details['serviceType']}</td></tr>
                        <tr><td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Requested Date:</strong></td><td style="padding: 8px 0; border-bottom: 1px solid #eee;">{details['inspectionDate']}</td></tr>
                        <tr><td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Notes:</strong></td><td style="padding: 8px 0; border-bottom: 1px solid #eee;">{details['notes'] if details['notes'] else 'None'}</td></tr>
                    </table>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=10) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, BUSINESS_EMAIL, msg.as_string())
        return True
    except Exception as e:
        print(f"[Email Error] Failed to dispatch internal company alert: {str(e)}")
        return False

# 4. CrewAI Environment & Model Configuration
api_key_from_env = os.getenv("OPENAI_API_KEY", "")

if api_key_from_env:
    os.environ["OPENAI_API_KEY"] = api_key_from_env

custom_llm = LLM(
    model="gpt-4o-mini",
    api_key=api_key_from_env
)

# 5. CrewAI Agent & Task Setup 
electrical_analyst = Agent(
    role="VoltShield Electrical Safety Expert",
    goal="Analyze reported electrical symptoms and prioritize risk levels.",
    backstory="An expert electrical engineer specializing in identifying hazards and triaging home electrical problems.",
    verbose=True,
    llm=custom_llm,
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

# 6. Application Routes (Endpoints)
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
        
        # Fire off real emails securely via Yandex SMTP SSL
        customer_email_sent = send_confirmation_email(data.email, data.fullName, booking_details)
        business_email_sent = send_business_notification_email(booking_details)
        
        return {
            "status": "success",
            "message": "Your booking has been received! Checking your notification logs.",
            "booking_id": f"VS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "emails_dispatched": {
                "customer": customer_email_sent,
                "business": business_email_sent
            }
        }
            
    except Exception as e:
        return {
            "status": "error",
            "message": "There was an error processing your booking.",
            "error": str(e)
        }
