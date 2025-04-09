from fastapi import FastAPI
from pydantic import BaseModel
from ticket_booking_agent.agent import TicketBookingAgent

app = FastAPI()
agent = TicketBookingAgent()

class Message(BaseModel):
    message: str

@app.post("/ticket/respond")
async def respond(message: Message):
    reply = agent.respond_to_user(message.message)
    return {"reply": reply}
