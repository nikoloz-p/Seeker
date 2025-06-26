import os
import requests

MAILERSEND_API_KEY = os.environ.get("MAILERSEND_API_KEY")

def send_email(to_email, subject, html_content):
    url = "https://api.mailersend.com/v1/email"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MAILERSEND_API_KEY}",
    }

    data = {
        "from": {
            "email": "your_verified_sender@example.com",  # replace with MailerSend verified domain email
            "name": "Seeker"
        },
        "to": [{"email": to_email}],
        "subject": subject,
        "html": html_content,
    }

    response = requests.post(url, headers=headers, json=data)
    return response.status_code, response.json()