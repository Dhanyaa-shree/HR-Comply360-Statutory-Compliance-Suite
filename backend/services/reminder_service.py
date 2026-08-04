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
    """Check all compliance due dates and send reminders"""
    with app.app_context():
        today = date.today()
        
        # Get all compliance that are not completed
        compliance_list = Compliance.query.filter(
            Compliance.status != 'Completed'
        ).all()
        
        # Get HR user
        hr_user = User.query.first()
        if not hr_user:
            print("⚠️ No HR user found to send reminders")
            return
        
        reminders_sent = 0
        
        for compliance in compliance_list:
            if not compliance.valid_date:
                continue
            
            days_until_due = (compliance.valid_date - today).days
            reminder_types = []
            
            # Determine which reminders to send
            if days_until_due == 30:
                reminder_types.append('30 Days')
            elif days_until_due == 15:
                reminder_types.append('15 Days')
            elif days_until_due == 7:
                reminder_types.append('7 Days')
            elif days_until_due == 3:
                reminder_types.append('3 Days')
            elif days_until_due == 1:
                reminder_types.append('1 Day')
            elif days_until_due == 0:
                reminder_types.append('Due Date')
            elif days_until_due < 0 and days_until_due > -7:
                reminder_types.append('Overdue')
            
            for reminder_type in reminder_types:
                # Check if reminder already sent today
                existing_log = EmailLog.query.filter(
                    EmailLog.compliance_id == compliance.id,
                    EmailLog.reminder_type == reminder_type,
                    db.func.date(EmailLog.sent_at) == today
                ).first()
                
                if not existing_log:
                    try:
                        subject = f"Compliance Reminder: {compliance.compliance_name} - {reminder_type}"
                        
                        # Send email
                        success = send_reminder_email(
                            app,
                            hr_user.email,
                            subject,
                            compliance,
                            days_until_due if days_until_due > 0 else 0
                        )
                        
                        # Log email
                        email_log = EmailLog(
                            user_id=hr_user.id,
                            compliance_id=compliance.id,
                            recipient_email=hr_user.email,
                            subject=subject,
                            message=f"Reminder for {compliance.compliance_name}",
                            reminder_type=reminder_type,
                            email_status='Sent' if success else 'Failed'
                        )
                        db.session.add(email_log)
                        
                        # Create notification
                        notification = Notification(
                            user_id=hr_user.id,
                            title=f"Compliance Reminder: {compliance.compliance_name}",
                            message=f"{reminder_type} reminder for {compliance.compliance_name}. Due: {compliance.valid_date.strftime('%d-%m-%Y')}",
                            type='Reminder',
                            compliance_id=compliance.id
                        )
                        db.session.add(notification)
                        
                        db.session.commit()
                        reminders_sent += 1
                        print(f"📧 Sent {reminder_type} reminder for: {compliance.compliance_name}")
                        
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