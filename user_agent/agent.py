from crewai import Agent
from groq import Groq
import os
import httpx
import json
from datetime import datetime
from shared.utils import generate_dummy_trip

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class UserAgent:
    def __init__(self):
        self.agent = Agent(
            role='User Agent',
            goal='Autonomously book a ticket by talking to booking agent',
            backstory='You are a smart autonomous assistant that understands and replies like a human.',
            model="llama3-70b-8192",
            verbose=True
        )
        self.api_url = "http://localhost:8000/ticket/respond"
        self.memory = []

    def chat_with_booking_agent(self, turns=6):
        conversation_log = []
        trip = generate_dummy_trip()

        # Initial user message
        current_user_msg = (
            f"Hi, I’d like to book a flight from {trip['from']} to {trip['to']} "
            f"on {trip['date']} at {trip['time']}. I prefer a window seat and vegetarian meal. "
            "Please share the options and book if possible."
        )

        for i in range(turns):
            self.memory.append({"role": "user", "content": current_user_msg})
            conversation_log.append({"user_agent": current_user_msg})

            try:
                response = httpx.post(self.api_url, json={"message": current_user_msg}, timeout=30.0)
                booking_reply = response.json()["reply"]
            except Exception as e:
                print(f"\n⚠️ Error calling booking agent: {e}")
                break

            print(f"\n🎫 Booking Agent [{i+1}]: {booking_reply}")
            self.memory.append({"role": "assistant", "content": booking_reply})
            conversation_log.append({"booking_agent": booking_reply})

            # Generate next intelligent user response
            reply_prompt = (
                "You are a helpful assistant trying to book a flight.\n\n"
                f"The booking agent said:\n{booking_reply}\n\n"
                "What should you say next to continue the booking?"
            )

            try:
                user_response = client.chat.completions.create(
                    messages=[{"role": "user", "content": reply_prompt}],
                    model="llama3-70b-8192",
                )
                current_user_msg = user_response.choices[0].message.content
            except Exception as e:
                print(f"\n⚠️ Error generating user agent reply: {e}")
                break

            print(f"\n🧑‍💼 User Agent [{i+1}]: {current_user_msg}")
            conversation_log.append({"user_agent": current_user_msg})

        self._save_conversation(conversation_log)

    def _save_conversation(self, log):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"user_agent/conversations/convo_{timestamp}.json"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as f:
            json.dump(log, f, indent=2)

        print(f"\n✅ Conversation saved to: {file_path}")
