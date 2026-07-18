import os
import resend
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Initialize FastAPI
app = FastAPI(title="Voltshield Electrical Backend")

# 🔒 FIX 1: Allow GitHub Pages to talk to Render without browser blocks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://amdiallo1.github.io"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows POST, GET, etc.
    allow_headers=["*"],
)

resend.api_key = os.getenv("RESEND_API_KEY")

# Data Schema (Matches your GitHub frontend form)
class Booking(BaseModel):
    fullName: str
    email: str
    phone: str
    serviceType: str
    inspectionDate: str
    notes: str

# Email Service Layer
def send_booking_email(booking: Booking, crew_analysis: str = ""):
    # We can inject what the Crew found right into the email html below!
    html_content = f"""
    <h3>⚡ New Booking Received via Voltshield</h3>
    <p><strong>Name:</strong> {booking.fullName}</p>
    <p><strong>Email:</strong> {booking.email}</p>
    <p><strong>Phone:</strong> {booking.phone}</p>
    <p><strong>Service:</strong> {booking.serviceType}</p>
    <p><strong>Date Request:</strong> {booking.inspectionDate}</p>
    <p><strong>Notes:</strong> {booking.notes}</p>
    """
    if crew_analysis:
        html_content += f"<hr><h4>🤖 CrewAI Agent Analysis:</h4><p>{crew_analysis}</p>"

    return resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": "amdiallo1@yandex.com", 
        "subject": f"New Booking: {booking.serviceType} - {booking.fullName}",
        "html": html_content
    })

# API Route
@app.post("/submit-booking")
async def submit_booking(booking: Booking):
    try:
        # 🤖 FIX 2: This is exactly where your CrewAI kickoff maps the inputs
        # If your Crew files are imported, you would uncomment and use this:
        # 
        # crew_inputs = {
        #     "customer_name": booking.fullName,
        #     "email": booking.email,
        #     "phone": booking.phone,
        #     "service_requested": booking.serviceType,
        #     "date": booking.inspectionDate,
        #     "client_notes": booking.notes
        # }
        # crew_result = your_voltshield_crew.kickoff(inputs=crew_inputs)
        # crew_analysis_text = str(crew_result)
        
        # For now, we pass an empty string until you drop your agent definitions in
        crew_analysis_text = "Crew processing placeholder (Ready to hook up your agents!)"

        # Send the email alert out with the details
        send_booking_email(booking, crew_analysis=crew_analysis_text)
        
        return {"status": "success", "message": "Booking received and agents notified!"}
        
    except Exception as e:
        print(f"DEBUG: Operation failed - {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
