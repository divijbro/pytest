from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import resend
import os
import datetime

app = Flask(__name__)
CORS(app)

mongo_uri = os.environ.get("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["mnmk_database"]
bookings_collection = db["bookings"]

resend_api_key = os.environ.get("RESEND_API_KEY")
resend = resend(resend_api_key)

@app.route("/")
def home():
    return "MNMK Backend Running 🚀"

@app.route("/send", methods=["POST"])
def send_booking():
    data = request.json

    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    message = data.get("message")

    booking_id = f"MNMK-{int(datetime.datetime.now().timestamp())}"

    booking_data = {
        "booking_id": booking_id,
        "name": name,
        "email": email,
        "phone": phone,
        "message": message,
        "status": "Pending",
        "created_at": datetime.datetime.utcnow()
    }

    bookings_collection.insert_one(booking_data)

    resend.emails.send({
        "from": "onboarding@resend.dev",
        "to": email,
        "subject": "Booking Request Received 🎉",
        "html": f"""
            <h2>Thank you for booking with MNMK Celebrations!</h2>
            <p>Your Booking ID: <strong>{booking_id}</strong></p>
            <p>We will contact you within 24 hours.</p>
        """
    })

    return jsonify({
        "success": True,
        "booking_id": booking_id
    })

if __name__ == "__main__":
    app.run(debug=True)