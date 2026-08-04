from app import app, mail
from flask_mail import Message

def test_email():
    with app.app_context():
        try:
            msg = Message(
                subject="🧪 Test Email from HR Comply360",
                recipients=["thangaraj4u@gmail.com"],
                body="✅ Your email is configured correctly! You will receive notifications on your phone."
            )
            mail.send(msg)
            print("✅ Test email sent successfully!")
            print("📧 Check: thangaraj4u@gmail.com")
            print("📱 Check your phone for notification!")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    test_email()