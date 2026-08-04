from flask import current_app
from flask_mail import Message
from app import mail

def send_reminder_email(app, recipient, subject, compliance, days_remaining):
    try:
        with app.app_context():
            msg = Message(
                subject=subject,
                recipients=[recipient]
            )
            
            # Determine reminder type from subject
            reminder_type = "Compliance Reminder"
            reminder_icon = "📋"
            urgency_color = '#10B981'
            
            if "First Reminder" in subject:
                reminder_type = "🔔 First Reminder"
                reminder_icon = "🔔"
                urgency_color = '#3B82F6'  # Blue
            elif "Second Reminder" in subject:
                reminder_type = "🔔 Second Reminder (5 Days Before)"
                reminder_icon = "🔔"
                urgency_color = '#F59E0B'  # Yellow
            elif "Third Reminder" in subject:
                reminder_type = "🔔 Third Reminder (2 Days Before)"
                reminder_icon = "🔔"
                urgency_color = '#EF4444'  # Red
            elif "30 Days" in subject:
                reminder_type = "📋 30 Days Reminder"
                urgency_color = '#10B981'  # Green
            elif "15 Days" in subject:
                reminder_type = "📋 15 Days Reminder"
                urgency_color = '#3B82F6'  # Blue
            elif "7 Days" in subject:
                reminder_type = "📋 7 Days Reminder"
                urgency_color = '#F59E0B'  # Yellow
            elif "3 Days" in subject or "1 Day" in subject:
                reminder_type = "📋 Urgent Reminder"
                urgency_color = '#EF4444'  # Red
            elif "Due Date" in subject:
                reminder_type = "⚠️ Due Date Reminder"
                urgency_color = '#EF4444'  # Red
            elif "Overdue" in subject:
                reminder_type = "🚨 Overdue Alert"
                urgency_color = '#EF4444'  # Red
            
            # Set urgency based on days remaining
            if days_remaining <= 2 and days_remaining >= 0:
                urgency_color = '#EF4444'  # Red - Urgent
            elif days_remaining <= 5:
                urgency_color = '#F59E0B'  # Yellow - Warning
            elif days_remaining <= 10:
                urgency_color = '#F97316'  # Orange - Caution
            
            # Get priority color
            priority_color = '#6B7280'
            if compliance.priority == 'High':
                priority_color = '#EF4444'
            elif compliance.priority == 'Medium':
                priority_color = '#F59E0B'
            elif compliance.priority == 'Low':
                priority_color = '#10B981'
            
            # Get status badge color
            status_color = '#6B7280'
            status_bg = '#F3F4F6'
            if compliance.status == 'Completed':
                status_color = '#065F46'
                status_bg = '#D1FAE5'
            elif compliance.status == 'Ongoing':
                status_color = '#92400E'
                status_bg = '#FEF3C7'
            elif compliance.status == 'Planned':
                status_color = '#1E40AF'
                status_bg = '#DBEAFE'
            elif compliance.status == 'Overdue':
                status_color = '#991B1B'
                status_bg = '#FEE2E2'
            
            msg.html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #2563EB, #4F46E5); color: white; padding: 25px; border-radius: 12px 12px 0 0; }}
                    .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 12px 12px; border: 1px solid #e5e7eb; }}
                    .field {{ margin: 12px 0; padding: 12px 16px; background: white; border-radius: 8px; border-left: 4px solid {urgency_color}; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
                    .label {{ font-weight: bold; color: #4B5563; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }}
                    .value {{ font-size: 16px; color: #111827; margin-top: 2px; }}
                    .badge-status {{ display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 500; background: {status_bg}; color: {status_color}; }}
                    .badge-priority {{ display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 500; background: {priority_color}20; color: {priority_color}; }}
                    .urgency-badge {{ background: {urgency_color}; color: white; padding: 8px 20px; border-radius: 20px; display: inline-block; font-size: 14px; font-weight: bold; }}
                    .days-remaining {{ font-size: 28px; font-weight: 800; color: {urgency_color}; }}
                    .footer {{ margin-top: 20px; padding: 15px; background: #f3f4f6; border-radius: 8px; text-align: center; font-size: 12px; color: #6B7280; }}
                    .action-box {{ background: #FEF2F2; padding: 15px; border-radius: 8px; border-left: 4px solid #EF4444; margin-top: 20px; }}
                    .action-box p {{ margin: 0; color: #991B1B; }}
                    .divider {{ border: none; border-top: 1px solid #e5e7eb; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2 style="margin: 0;">{reminder_icon} HR Comply360</h2>
                        <p style="margin: 5px 0 0; opacity: 0.9;">Centralized HR Compliance Portal</p>
                    </div>
                    <div class="content">
                        <div style="text-align: center; margin-bottom: 20px;">
                            <span class="urgency-badge">{reminder_type}</span>
                        </div>
                        
                        <h3 style="margin-top: 0; color: #1a1a2e;">📌 Compliance Details</h3>
                        
                        <div class="field">
                            <div class="label">📌 Compliance Name</div>
                            <div class="value"><strong>{compliance.compliance_name}</strong></div>
                        </div>
                        
                        <div class="field">
                            <div class="label">🏛️ Authority</div>
                            <div class="value">{compliance.authority}</div>
                        </div>
                        
                        <div class="field">
                            <div class="label">📅 Due Date</div>
                            <div class="value"><strong>{compliance.valid_date.strftime('%d-%m-%Y') if compliance.valid_date else 'N/A'}</strong></div>
                        </div>
                        
                        <div class="field">
                            <div class="label">⏰ Days Remaining</div>
                            <div class="value"><span class="days-remaining">{days_remaining}</span> <span style="font-size: 16px; color: #6B7280;">days</span></div>
                        </div>
                        
                        <div class="field">
                            <div class="label">📊 Status</div>
                            <div class="value"><span class="badge-status">{compliance.status}</span></div>
                        </div>
                        
                        <div class="field">
                            <div class="label">⚡ Priority</div>
                            <div class="value"><span class="badge-priority">{compliance.priority}</span></div>
                        </div>
                        
                        <div class="field">
                            <div class="label">📋 Category</div>
                            <div class="value">{compliance.category}</div>
                        </div>
                        
                        <hr class="divider">
                        
                        <div class="action-box">
                            <p>⚠️ <strong>Action Required:</strong> Please complete this compliance by the due date.</p>
                        </div>
                        
                        <div style="margin-top: 15px; background: #F3F4F6; padding: 12px; border-radius: 8px;">
                            <p style="margin: 0; font-size: 13px; color: #4B5563;">
                                💡 <strong>Reminder Schedule:</strong><br>
                                • Reminder 1: Manual date set by HR<br>
                                • Reminder 2: 5 days before due date<br>
                                • Reminder 3: 2 days before due date
                            </p>
                        </div>
                    </div>
                    <div class="footer">
                        <p>This is an automated reminder from HR Comply360.</p>
                        <p style="margin: 0;">Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            mail.send(msg)
            print(f"✅ Email sent to {recipient}: {subject}")
            return True
            
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        return False