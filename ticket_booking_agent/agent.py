# from crewai import Agent
# from groq import Groq
# import os

# client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# class TicketBookingAgent:
#     def __init__(self):
#         self.agent = Agent(
#             role='Ticket Booking Agent',
#             goal='Book travel tickets based on requests',
#             backstory='You are a helpful agent who handles ticket bookings for user agents via REST.',
#             model="llama3-70b-8192",
#             verbose=True
#         )
#         self.memory = []

#     def respond_to_user(self, message: str) -> str:
#         self.memory.append({"role": "user", "content": message})
#         response = client.chat.completions.create(
#             messages=self.memory,
#             model="llama3-70b-8192",
#         )
#         reply = response.choices[0].message.content
#         self.memory.append({"role": "assistant", "content": reply})
#         return reply


from groq import Groq
import os
import random
from datetime import datetime, timedelta

# Replace with os.getenv("GROQ_API_KEY") for production
client = Groq(api_key="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")

class TicketBookingAgent:
    def __init__(self):
        self.reset_booking()

    def reset_booking(self):
        self.memory = []
        self.confirmed = False
        self.awaiting_confirmation = False
        travel_date = datetime.now() + timedelta(days=2)
        self.flight_details = {
            "from": "Ahmedabad",
            "to": "Delhi",
            "date": travel_date.strftime("%Y-%m-%d"),
            "time": "16:00",
            "arrival_time": "18:15",
            "flight_number": "DL123",
            "seat": "10A",
            "meal": "Vegetarian Meal",
            "aircraft": "Airbus A320",
            "pnr": None,
            "price": "₹3,500",
            "insurance": None,
        }

    def respond_to_user(self, message: str) -> str:
        self.memory.append({"role": "user", "content": message})
        lower = message.lower()

        if any(kw in lower for kw in ["start over", "book new", "book another", "new booking", "another flight", "book from"]):
            self.reset_booking()
            reply = self._get_greeting()
        elif not self.confirmed:
            if self.awaiting_confirmation and any(w in lower for w in ["yes", "confirm", "book now"]):
                self.confirmed = True
                self.flight_details["pnr"] = self._generate_pnr()
                reply = self._get_confirmation_message()
            elif any(w in lower for w in ["book", "flight", "seat", "window", "meal", "vegetarian"]):
                reply = self._get_offer_message()
                self.awaiting_confirmation = True
            else:
                reply = self._respond_smartly(message)
        else:
            reply = self._handle_post_confirmation(message)

        self.memory.append({"role": "assistant", "content": reply})
        return reply

    def _handle_post_confirmation(self, message):
        lower = message.lower()
        d = self.flight_details

        if any(k in lower for k in ["book another", "book from", "new booking", "new flight", "delhi to mumbai"]):
            self.reset_booking()
            return self._get_greeting()

        # 🧠 Try Groq LLM for smart follow-up
        groq_reply = self._groq_post_booking_response(message)
        if groq_reply:
            return groq_reply

        # 🔁 fallback basic replies
        if "pnr" in lower:
            return f"Your PNR is **{d['pnr']}**."
        if "meal" in lower:
            return f"Your meal preference is confirmed as: **{d['meal']}**."
        if "seat" in lower and any(w in lower for w in ["available", "choose", "select"]):
            return (
                "Here are the available seats:\n"
                "10A (Window) ✅\n"
                "10B (Middle)\n"
                "10C (Aisle)\n"
                "11A (Window - Extra Legroom) 💺\n"
                "Would you like to upgrade to an extra legroom seat for ₹500?"
            )
        if "seat" in lower and "confirm" in lower:
            return f"Your confirmed seat is **{d['seat']}** (Window)."
        if "upgrade" in lower or "extra legroom" in lower:
            return "You can upgrade to an extra legroom seat for ₹500. Would you like to proceed?"
        if "baggage" in lower:
            return "You're allowed **1 cabin bag (7kg)** and **1 checked bag (15kg)**. Additional luggage is ₹400 per 5kg."
        if "class" in lower:
            return "Your booking is in **Economy Class**."
        if "flight" in lower and any(w in lower for w in ["details", "times", "summary"]):
            return (
                f"Here's your flight summary:\n\n"
                f"🛫 {d['from']} ➡️ {d['to']}\n"
                f"📅 Date: {d['date']} | Departure: {d['time']} | Arrival: {d['arrival_time']}\n"
                f"✈️ Flight: {d['flight_number']} | Aircraft: {d['aircraft']}\n"
                f"💺 Seat: {d['seat']} | 🍽️ Meal: {d['meal']}\n"
                f"💰 Fare: {d['price']}\n"
                f"🛡️ Travel Insurance: {d['insurance'] if d['insurance'] else 'Not added'}\n"
                f"🔐 PNR: {d['pnr']}"
            )
        if "nonstop" in lower or "layover" in lower:
            return "This is a **non-stop flight** from Ahmedabad to Delhi. No layovers included."
        if "ticket" in lower or "email" in lower:
            return "Your e-ticket has been sent to your registered email. You can also collect a printed boarding pass at the airport for free."
        if "insurance" in lower:
            if "yes" in lower or "add" in lower:
                d["insurance"] = "Yes"
                return "✅ Travel insurance added for ₹300. Your total fare is now ₹3,800."
            elif "no" in lower or "decline" in lower:
                d["insurance"] = "No"
                return "No problem. Your fare remains ₹3,500."
            else:
                return "Would you like to add travel insurance for ₹300?"

        return (
            "Let me know if you’d like to:\n"
            "- View seat options 💺\n"
            "- Add insurance 🛡️\n"
            "- Upgrade your seat ✨\n"
            "- Get flight summary 🧾\n"
            "- Or start a **new booking** by saying 'book another flight'."
        )

    def _groq_post_booking_response(self, message):
        d = self.flight_details
        prompt = (
            "You are a helpful and realistic flight booking assistant. The user has already booked this flight:\n\n"
            f"🛫 From: {d['from']} ➡️ {d['to']}\n"
            f"📅 Date: {d['date']} at {d['time']} | Arrival: {d['arrival_time']}\n"
            f"✈️ Flight: {d['flight_number']} | Aircraft: {d['aircraft']}\n"
            f"💺 Seat: {d['seat']} | 🍽️ Meal: {d['meal']}\n"
            f"💰 Price: {d['price']}\n"
            f"🔐 PNR: {d['pnr']}\n\n"
            "Recent conversation:\n" +
            "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in self.memory[-4:]]) +
            f"\n\nNow answer this user query as the assistant:\nUser: {message}"
        )
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192",
            )
            content = response.choices[0].message.content.strip()
            return content if content else None
        except Exception as e:
            print(f"[Groq Error] {e}")
            return None

    def _respond_smartly(self, message):
        prompt = (
            "You are a friendly airline booking assistant. Based on the conversation so far:\n\n"
            f"Flight: {self.flight_details['flight_number']}, From {self.flight_details['from']} to {self.flight_details['to']} on {self.flight_details['date']} at {self.flight_details['time']}.\n"
            f"Seat: {self.flight_details['seat']}, Meal: {self.flight_details['meal']}, Aircraft: {self.flight_details['aircraft']}, Price: {self.flight_details['price']}.\n\n"
            "Conversation history:\n" +
            "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in self.memory[-4:]]) +
            f"\n\nUser: {message}\nAssistant:"
        )
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192",
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[Groq Error] {e}")
            return "Sorry, there was an error processing your request."

    def _generate_pnr(self):
        return "PNR" + ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6))

    def _get_greeting(self):
        return (
            "Hi! Let's start your new flight booking ✈️\n"
            "Please tell me your **departure city, destination, and date**."
        )

    def _get_offer_message(self):
        d = self.flight_details
        return (
            f"Here's a flight you can book:\n\n"
            f"🛫 **Flight**: {d['flight_number']} | {d['aircraft']}\n"
            f"📅 **Date**: {d['date']} | **Time**: {d['time']}\n"
            f"🛬 **Arrival**: {d['arrival_time']}\n"
            f"💺 **Seat**: {d['seat']} (Window)\n"
            f"🍽️ **Meal**: {d['meal']}\n"
            f"💰 **Fare**: {d['price']}\n\n"
            "Reply with **YES** to confirm and book."
        )

    def _get_confirmation_message(self):
        d = self.flight_details
        total = "₹3,800" if d["insurance"] == "Yes" else d["price"]
        return (
            "**✅ Booking Confirmed!**\n\n"
            f"🔐 PNR: {d['pnr']}\n"
            f"🛫 {d['from']} ➡️ {d['to']}\n"
            f"📅 {d['date']} | Departure: {d['time']} | Arrival: {d['arrival_time']}\n"
            f"💺 Seat: {d['seat']} | 🍽️ Meal: {d['meal']}\n"
            f"💰 Total Fare: {total}\n\n"
            "✅ Your ticket has been emailed. Arrive 2 hrs early with valid ID. Safe travels!"
        )
