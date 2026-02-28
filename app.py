import psycopg2
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from resend import Resend
import datetime

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get("DB_URL")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")

resend = Resend(RESEND_API_KEY)

@app.route("/")
def home():
    return "Backend Running 🚀"

@app.route("/send", methods=["POST"])
def send_booking():
    data = request.json

    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    message = data.get("message")

    booking_id = f"MNMK-{int(datetime.datetime.now().timestamp())}"

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO bookings (booking_id, name, email, phone, message, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (booking_id, name, email, phone, message, "false"))

        conn.commit()
        cursor.close()
        conn.close()

        resend.emails.send({
            "from": "onboarding@resend.dev",
            "to": [email],   # MUST be a list
            "subject": "Booking Request Received 🎉",
            "html": f"""
                <h2>🎉 Thank You for Booking with MNMK Celebrations!</h2>
                <p>Your Booking ID: <strong>{booking_id}</strong></p>
                <p>We will contact you within 24 hours.</p>
    """
})

        return jsonify({
            "success": True,
            "booking_id": booking_id
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"success": False}), 500


if __name__ == "__main__":
    app.run(debug=True)



