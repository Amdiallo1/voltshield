from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

app = FastAPI()

# Enable CORS for your frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class BookingRequest(BaseModel):
    fullName: str
    email: str
    phone: str
    serviceType: str
    inspectionDate: str
    notes: str = ""

# Email configuration (use environment variables for security)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your-email@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your-app-password")
BUSINESS_EMAIL = os.getenv("BUSINESS_EMAIL", "voltshield@example.com")

def send_confirmation_email(customer_email: str, customer_name: str, booking_details: dict):
    """Send confirmation email to customer"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = customer_email
        msg['Subject'] = "VoltShield Compliance - Booking Confirmation"
        
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #2c3e50;">
                <h2 style="color: #005bbb;">Thank You, {customer_name}!</h2>
                <p>We've received your booking request for VoltShield Compliance electrical safety inspection.</p>
                
                <h3 style="color: #005bbb;">Booking Details:</h3>
                <ul>
                    <li><strong>Service:</strong> {booking_details['serviceType']}</li>
                    <li><strong>Preferred Date:</strong> {booking_details['inspectionDate']}</li>
                    <li><strong>Phone:</strong> {booking_details['phone']}</li>
                </ul>
                
                <p>Our team will review your request and contact you within 24 hours to confirm your inspection appointment.</p>
                
                <p style="color: #7a869a; font-size: 12px;">
                    <strong>VoltShield Compliance Team</strong><br>
                    Professional Electrical Safety Inspections<br>
                    OSHA 70E Compliance | NICET Certified Inspectors
                </p>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending confirmation email: {e}")
        return False

def send_business_notification_email(booking_details: dict):
    """Send notification email to business owner"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = BUSINESS_EMAIL
        msg['Subject'] = f"New Booking Request - {booking_details['fullName']}"
        
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #2c3e50;">
                <h2 style="color: #005bbb;">New Inspection Booking Request</h2>
                <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h3>Customer Information:</h3>
                <ul>
                    <li><strong>Name:</strong> {booking_details['fullName']}</li>
                    <li><strong>Email:</strong> {booking_details['email']}</li>
                    <li><strong>Phone:</strong> {booking_details['phone']}</li>
                </ul>
                
                <h3>Booking Details:</h3>
                <ul>
                    <li><strong>Service Type:</strong> {booking_details['serviceType']}</li>
                    <li><strong>Preferred Date:</strong> {booking_details['inspectionDate']}</li>
                    <li><strong>Notes:</strong> {booking_details['notes'] or 'None'}</li>
                </ul>
                
                <p style="background-color: #f7f9fc; padding: 15px; border-left: 4px solid #005bbb;">
                    <strong>Action Required:</strong> Please contact the customer to confirm this appointment.
                </p>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending business notification email: {e}")
        return False

@app.get("/")
def home():
    return {"message": "VoltShield Compliance Backend is Online!", "status": "ready"}

@app.post("/submit-booking")
async def submit_booking(data: BookingRequest):
    """Handle booking form submission"""
    try:
        booking_details = {
            'fullName': data.fullName,
            'email': data.email,
            'phone': data.phone,
            'serviceType': data.serviceType,
            'inspectionDate': data.inspectionDate,
            'notes': data.notes
        }
        
        # Send confirmation email to customer
        customer_email_sent = send_confirmation_email(data.email, data.fullName, booking_details)
        
        # Send notification email to business
        business_email_sent = send_business_notification_email(booking_details)
        
        if customer_email_sent and business_email_sent:
            return {
                "status": "success",
                "message": "Your booking has been submitted successfully! Check your email for confirmation.",
                "booking_id": f"VS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
        else:
            return {
                "status": "success",
                "message": "Your booking has been received! Our team will contact you shortly.",
                "booking_id": f"VS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
            
    except Exception as e:
        print(f"Error processing booking: {e}")
        return {
            "status": "error",
            "message": "There was an error processing your booking. Please try again.",
            "error": str(e)
        }

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "voltshield-backend"}
