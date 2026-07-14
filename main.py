from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# This allows your website to securely talk to this backend code
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
def home():
    return {"message": "CrewAI Electrical Backend is Online!"}

@app.post("/run-crew")
async def trigger_crew(data: CustomerRequest):
    # This prepares the inputs for your CrewAI agents
    inputs = {
        "customer_name": data.customer_name,
        "email": data.email,
        "issue_description": data.issue_description
    }
    
    # Simple success response to test the connection
    result_text = f"Hello {data.customer_name}! We received your request about: '{data.issue_description}'. Our AI Crew is analyzing this for our electricians."
    
    return {"status": "success", "output": result_text}
