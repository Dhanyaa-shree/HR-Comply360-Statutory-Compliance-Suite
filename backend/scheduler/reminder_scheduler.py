from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, date, timedelta
from database.db import db
from models.compliance import Compliance
from models.email_log import EmailLog
from models.notification import Notification
from models.user import User
from services.email_service import send_reminder_email

scheduler = BackgroundScheduler()

def check_reminders(app):
    """Check all compliance due dates and send custom reminders"""
    with app.app_context():
        today = date.today()
        
        # Get all compliance that are not completed
        compliance_list = Compliance.query.filter(
            Compliance.status != 'Completed'
        ).all()
        
        # Get all HR users (instead of just first)
        hr_users = User.query.all()
        if not hr_users:
            print("⚠️ No HR users found to send reminders")
            return
        
        reminders_sent = 0
        
        for compliance in compliance_list:
            if not compliance.valid_date:
                continue
            
            valid_date = compliance.valid_date
            
            # Auto-calculate reminder 2 and 3 dates
            compliance.reminder_2_date = valid_date - timedelta(days=5)
            compliance.reminder_3_date = valid_date - timedelta(days=2)
            
            # If reminder_1_date is not set, set default (30 days before)
            if not compliance.reminder_1_date:
                compliance.reminder_1_date = valid_date - timedelta(days=30)
            
            db.session.commit()
            
            # Check each reminder type
            reminders_to_send = []
            
            # Reminder 1: Manual date set by HR
            if compliance.reminder_1_date and not compliance.reminder_1_sent:
                if today >= compliance.reminder_1_date:
                    days_until_due = (valid_date - today).days
                    reminders_to_send.append({
                        'type': 'First Reminder',
                        'days_until_due': days_until_due if days_until_due > 0 else 0,
                        'sent_field': 'reminder_1_sent'
                    })
            
            # Reminder 2: 5 days before due date
            if compliance.reminder_2_date and not compliance.reminder_2_sent:
                if today >= compliance.reminder_2_date:
                    days_until_due = (valid_date - today).days
                    reminders_to_send.append({
                        'type': 'Second Reminder (5 Days Before)',
                        'days_until_due': days_until_due if days_until_due > 0 else 0,
                        'sent_field': 'reminder_2_sent'
                    })
            
            # Reminder 3: 2 days before due date
            if compliance.reminder_3_date and not compliance.reminder_3_sent:
                if today >= compliance.reminder_3_date:
                    days_until_due = (valid_date - today).days
                    reminders_to_send.append({
                        'type': 'Third Reminder (2 Days Before)',
                        'days_until_due': days_until_due if days_until_due > 0 else 0,
                        'sent_field': 'reminder_3_sent'
                    })
            
            # Send reminders to all HR users
            for reminder in reminders_to_send:
                # Check if reminder already sent today
                existing_log = EmailLog.query.filter(
                    EmailLog.compliance_id == compliance.id,
                    EmailLog.reminder_type == reminder['type'],
                    db.func.date(EmailLog.sent_at) == today
                ).first()
                
                if not existing_log:
                    try:
                        # Send to all HR users
                        for hr_user in hr_users:
                            subject = f"{reminder['type']}: {compliance.compliance_name}"
                            
                            # Send email
                            success = send_reminder_email(
                                app,
                                hr_user.email,
                                subject,
                                compliance,
                                reminder['days_until_due']
                            )
                            
                            # Log email
                            email_log = EmailLog(
                                user_id=hr_user.id,
                                compliance_id=compliance.id,
                                recipient_email=hr_user.email,
                                subject=subject,
                                message=f"{reminder['type']} for {compliance.compliance_name}",
                                reminder_type=reminder['type'],
                                email_status='Sent' if success else 'Failed'
                            )
                            db.session.add(email_log)
                            
                            # Create in-app notification
                            notification = Notification(
                                user_id=hr_user.id,
                                title=f"Compliance Reminder: {compliance.compliance_name}",
                                message=f"{reminder['type']}: {compliance.compliance_name}. Due: {compliance.valid_date.strftime('%d-%m-%Y')}",
                                type='Reminder',
                                compliance_id=compliance.id
                            )
                            db.session.add(notification)
                        
                        # Mark reminder as sent
                        setattr(compliance, reminder['sent_field'], True)
                        db.session.commit()
                        reminders_sent += 1
                        print(f"📧 Sent {reminder['type']} for: {compliance.compliance_name}")
                        
                    except Exception as e:
                        print(f"❌ Error sending reminder for {compliance.compliance_name}: {str(e)}")
                        db.session.rollback()
        
        if reminders_sent > 0:
            print(f"✅ Sent {reminders_sent} reminders today")
        else:
            print("📭 No reminders to send today")

def start_scheduler(app):
    """Start the reminder scheduler"""
    try:
        scheduler.add_job(
            lambda: check_reminders(app),
            trigger=CronTrigger(hour=8, minute=0),
            id='reminder_job',
            replace_existing=True
        )
        scheduler.start()
        print("🔄 Reminder scheduler started - running daily at 8:00 AM")
    except Exception as e:
        print(f"❌ Failed to start scheduler: {str(e)}")

def stop_scheduler():
    """Stop the reminder scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        print("⏹️ Reminder scheduler stopped")

def run_reminders_now(app):
    """Run reminders immediately (for testing)"""
    print("🚀 Running reminders immediately...")
    check_reminders(app)
    print("✅ Reminder check completed")