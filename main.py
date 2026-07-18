import os
import resend
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Initialize
app = FastAPI()
resend.api_key = os.getenv("RESEND_API_KEY")

# Data Schema
class Booking(BaseModel):
    fullName: str
    email: str
    phone: str
    serviceType: str
    inspectionDate: str
    notes: str

# Email Service Layer
def send_booking_email(booking: Booking):
    return resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": "amdiallo1@yandex.com", # Update this
        "subject": f"New Booking: {booking.serviceType}",
        "html": f"<p><strong>Name:</strong> {booking.fullName}<br><strong>Service:</strong> {booking.serviceType}</p>"
    })

# API Route
@app.post("/submit-booking")
async def submit_booking(booking: Booking):
    try:
        send_booking_email(booking)
        return {"status": "success"}
    except Exception as e:
        # This keeps the error logged in Render but returns a clean response
        print(f"DEBUG: Email failed - {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
