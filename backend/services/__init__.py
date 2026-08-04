# This file makes the services folder a Python package
from .email_service import send_reminder_email
from .reminder_service import start_scheduler