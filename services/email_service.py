import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from datetime import datetime
import os
from environment import (
    SMTP_SERVER, SMTP_PORT, SMTP_USERNAME,
    SMTP_PASSWORD, FROM_EMAIL, FROM_NAME
)


class EmailService:
    """Service for sending email notifications"""

    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = int(SMTP_PORT)
        self.smtp_username = SMTP_USERNAME
        self.smtp_password = SMTP_PASSWORD
        self.from_email = FROM_EMAIL
        self.from_name = FROM_NAME
    
    def _clean_header(self, value: str) -> str:

        if not value:
            return value
        return (
            value
            .replace('\xa0', ' ')
            .replace('\u200b', '')  # zero-width space
            .strip()
        )


    def send_email(self, to_emails, subject, html_content, text_content=None):
        try:
            msg = MIMEMultipart('alternative')
            
            subject = self._clean_header(subject)
            from_name = self._clean_header(self.from_name)
            from_email = self._clean_header(self.from_email)
            to_emails = [self._clean_header(e) for e in to_emails]

            # ✅ UTF-8 safe headers
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = formataddr((
                str(Header(self.from_name, 'utf-8')),
                self.from_email
            ))
            msg['To'] = ', '.join(to_emails)

            # Clean NBSP defensively
            if text_content:
                text_content = text_content.replace('\xa0', ' ')
                msg.attach(MIMEText(text_content, 'plain', 'utf-8'))

            html_content = html_content.replace('\xa0', ' ')
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                # server.send_message(msg)
                server.sendmail(
                from_email,
                to_emails,
                msg.as_bytes(policy=SMTPUTF8)
            )

            print("✅ Email sent successfully")
            return True, None

        except Exception as e:
            print("❌ Email send failed:", str(e))
            return False, str(e)

    # ---------------- ALERT EMAIL ---------------- #

    def send_no_receipts_alert(self, to_emails, date):
        date_str = date.strftime('%B %d, %Y')
        day_name = date.strftime('%A')

        subject = f"⚠️ No Receipts Generated - {date_str}"

        text_content = f"""
No Receipt Alert

Date: {date_str} ({day_name})

No receipts were generated today.

---
This is an automated message from BKK Print Service
        """

        html_content = f"""
<!DOCTYPE html>
<html>
<body>
<h2>⚠️ No Receipts Generated</h2>
<p><strong>Date:</strong> {date_str} ({day_name})</p>
<p>No receipts were generated for this day.</p>
</body>
</html>
        """

        return self.send_email(to_emails, subject, html_content, text_content)

    # ---------------- DAILY SUMMARY ---------------- #

    def send_daily_summary(self, to_emails, date, summary_data, currency):
        date_str = date.strftime('%B %d, %Y')
        day_name = date.strftime('%A')

        subject = f"📊 Daily Summary - {date_str}"

        total_receipts = summary_data.get('total_receipts', 0)
        total_revenue = summary_data.get('total_revenue', 0)

        text_content = f"""
Daily Summary Report

Date: {date_str} ({day_name})

Total Receipts: {total_receipts}
Total Revenue: {currency}{total_revenue:,.2f}
        """

        html_content = f"""
<!DOCTYPE html>
<html>
<body>
<h2>📊 Daily Summary</h2>
<p><strong>Date:</strong> {date_str} ({day_name})</p>
<ul>
    <li>Total Receipts: {total_receipts}</li>
    <li>Total Revenue: {currency}{total_revenue:,.2f}</li>
    <li>Avg / Receipt: {currency}{(total_revenue / total_receipts if total_receipts else 0):,.2f}</li>
</ul>
</body>
</html>
        """

        return self.send_email(to_emails, subject, html_content, text_content)

    def send_daily_summary(self, to_emails, date, summary_data, currency):
        """
        Send daily summary email with receipt statistics
        """
        date_str = date.strftime('%B %d, %Y')
        day_name = date.strftime('%A')

        subject = f"📊 Daily Summary - {date_str}"

        total_receipts = summary_data.get('total_receipts', 0)
        total_revenue = summary_data.get('total_revenue', 0)

        # ---------- Plain Text ----------
        text_content = f"""
    Daily Summary Report

    Date: {date_str} ({day_name})

    Summary:
    - Total Receipts: {total_receipts}
    - Total Revenue: {currency}{total_revenue:,.2f}

    ---
    This is an automated message from BKK Print Service
        """

        # ---------- HTML ----------
        html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            .header {{
                background-color: #4CAF50;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: white;
                padding: 30px;
                border-radius: 0 0 5px 5px;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin: 20px 0;
            }}
            .stat-card {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                text-align: center;
            }}
            .stat-value {{
                font-size: 24px;
                font-weight: bold;
                color: #4CAF50;
                margin: 10px 0;
            }}
            .stat-label {{
                color: #666;
                font-size: 14px;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                color: #666;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>📊 Daily Summary Report</h2>
                <p>{date_str} ({day_name})</p>
            </div>
            <div class="content">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">Total Receipts</div>
                        <div class="stat-value">{total_receipts}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Total Revenue</div>
                        <div class="stat-value">{currency}{total_revenue:,.2f}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Avg per Receipt</div>
                        <div class="stat-value">
                            {currency}{(total_revenue / total_receipts if total_receipts else 0):,.2f}
                        </div>
                    </div>
                </div>
            </div>
            <div class="footer">
                <p>
                    This is an automated message from BKK Print Service.<br>
                    Please do not reply to this email.
                </p>
            </div>
        </div>
    </body>
    </html>
        """

        return self.send_email(to_emails, subject, html_content, text_content)

# import smtplib
# from email.message import EmailMessage
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from datetime import datetime
# import os
# from environment import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, FROM_EMAIL, FROM_NAME
# class EmailService:
#     """Service for sending email notifications"""
    
#     def __init__(self):
#         self.smtp_server = SMTP_SERVER
#         self.smtp_port = int(SMTP_PORT)
#         self.smtp_username = SMTP_USERNAME
#         self.smtp_password = SMTP_PASSWORD
#         self.from_email = FROM_EMAIL
#         self.from_name = FROM_NAME
    
#     def send_email(self, to_emails, subject, html_content, text_content=None):
#         """
#         Send email to multiple recipients
        
#         Args:
#             to_emails (list): List of recipient email addresses
#             subject (str): Email subject
#             html_content (str): HTML email body
#             text_content (str): Plain text email body (optional)
        
#         Returns:
#             tuple: (success: bool, error: str or None)
#         """
#         try:
#             # Create message
#             msg = MIMEMultipart('alternative')
#             msg['Subject'] = subject
#             msg['From'] = f"{self.from_name} <{self.from_email}>"
#             msg['To'] = ', '.join(to_emails)
            
#             # Attach text and HTML parts
#             if text_content:
#                 part1 = MIMEText(text_content, 'plain')
#                 msg.attach(part1)
            
#             part2 = MIMEText(html_content, 'html')
#             msg.attach(part2)
            
#             # Send email
#             with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
#                 server.starttls()
#                 server.login(self.smtp_username, self.smtp_password)
#                 server.send_message(msg)
            
#             return True, None
            
#         except Exception as e:
#             return False, str(e)
    
#     def send_no_receipts_alert(self, to_emails, date):
#         """
#         Send alert email when no receipts are found for a day
        
#         Args:
#             to_emails (list): List of recipient email addresses
#             date (datetime): Date for which no receipts were found
        
#         Returns:
#             tuple: (success: bool, error: str or None)
#         """
#         date_str = date.strftime('%B %d, %Y')
#         day_name = date.strftime('%A')
        
#         subject = f"⚠️ No Receipts Generated - {date_str}"
        
#         # Plain text version
#         text_content = f"""
# No Receipt Alert

# Date: {date_str} ({day_name})

# No receipts were generated today. This is an automated notification to ensure you're aware of the day's activity.

# If this is expected (e.g., holiday, closed day), please disregard this message.
# Otherwise, you may want to verify system operations.

# ---
# This is an automated message from BKK Print Service
#         """
        
#         # HTML version
#         html_content = f"""
# <!DOCTYPE html>
# <html>
# <head>
#     <style>
#         body {{
#             font-family: Arial, sans-serif;
#             line-height: 1.6;
#             color: #333;
#         }}
#         .container {{
#             max-width: 600px;
#             margin: 0 auto;
#             padding: 20px;
#             background-color: #f9f9f9;
#         }}
#         .header {{
#             background-color: #ff6b6b;
#             color: white;
#             padding: 20px;
#             text-align: center;
#             border-radius: 5px 5px 0 0;
#         }}
#         .content {{
#             background-color: white;
#             padding: 30px;
#             border-radius: 0 0 5px 5px;
#         }}
#         .alert-icon {{
#             font-size: 48px;
#             margin-bottom: 10px;
#         }}
#         .date-box {{
#             background-color: #fff3cd;
#             border-left: 4px solid #ffc107;
#             padding: 15px;
#             margin: 20px 0;
#         }}
#         .footer {{
#             text-align: center;
#             margin-top: 20px;
#             color: #666;
#             font-size: 12px;
#         }}
#     </style>
# </head>
# <body>
#     <div class="container">
#         <div class="header">
#             <div class="alert-icon">⚠️</div>
#             <h2>No Receipts Generated Alert</h2>
#         </div>
#         <div class="content">
#             <div class="date-box">
#                 <strong>Date:</strong> {date_str} ({day_name})
#             </div>
            
#             <p>This is an automated notification to inform you that <strong>no receipts were generated</strong> on the above date.</p>
            
#             <p>If this is expected (e.g., holiday, store closed, etc.), please disregard this message.</p>
            
#             <p>Otherwise, you may want to:</p>
#             <ul>
#                 <li>Verify system operations</li>
#                 <li>Check if staff are properly recording transactions</li>
#                 <li>Review any potential system issues</li>
#             </ul>
#         </div>
#         <div class="footer">
#             <p>This is an automated message from BKK Print Service.<br>
#             Please do not reply to this email.</p>
#         </div>
#     </div>
# </body>
# </html>
#         """
        
#         return self.send_email(to_emails, subject, html_content, text_content)
    
#     def send_daily_summary(self, to_emails, date, summary_data, currency):
#         """
#         Send daily summary email with receipt statistics
        
#         Args:
#             to_emails (list): List of recipient email addresses
#             date (datetime): Date of the summary
#             summary_data (dict): Dictionary containing summary statistics
        
#         Returns:
#             tuple: (success: bool, error: str or None)
#         """
#         date_str = date.strftime('%B %d, %Y')
#         day_name = date.strftime('%A')
        
#         subject = f"📊 Daily Summary - {date_str}"
        
#         total_receipts = summary_data.get('total_receipts', 0)
#         total_revenue = summary_data.get('total_revenue', 0)
#         # total_items = summary_data.get('total_items', 0)
        
#         # Plain text version
#         text_content = f"""
# Daily Summary Report

# Date: {date_str} ({day_name})

# Summary:
# - Total Receipts: {total_receipts}
# - Total Revenue: {currency}{total_revenue:,.2f}

# ---
# This is an automated message from BKK Print Service
#         """
        
#         # HTML version
#         html_content = f"""
# <!DOCTYPE html>
# <html>
# <head>
#     <style>
#         body {{
#             font-family: Arial, sans-serif;
#             line-height: 1.6;
#             color: #333;
#         }}
#         .container {{
#             max-width: 600px;
#             margin: 0 auto;
#             padding: 20px;
#             background-color: #f9f9f9;
#         }}
#         .header {{
#             background-color: #4CAF50;
#             color: white;
#             padding: 20px;
#             text-align: center;
#             border-radius: 5px 5px 0 0;
#         }}
#         .content {{
#             background-color: white;
#             padding: 30px;
#             border-radius: 0 0 5px 5px;
#         }}
#         .stats-grid {{
#             display: grid;
#             grid-template-columns: 1fr 1fr;
#             gap: 15px;
#             margin: 20px 0;
#         }}
#         .stat-card {{
#             background-color: #f8f9fa;
#             padding: 15px;
#             border-radius: 5px;
#             text-align: center;
#         }}
#         .stat-value {{
#             font-size: 24px;
#             font-weight: bold;
#             color: #4CAF50;
#             margin: 10px 0;
#         }}
#         .stat-label {{
#             color: #666;
#             font-size: 14px;
#         }}
#         .footer {{
#             text-align: center;
#             margin-top: 20px;
#             color: #666;
#             font-size: 12px;
#         }}
#     </style>
# </head>
# <body>
#     <div class="container">
#         <div class="header">
#             <h2>📊 Daily Summary Report</h2>
#             <p>{date_str} ({day_name})</p>
#         </div>
#         <div class="content">
#             <div class="stats-grid">
#                 <div class="stat-card">
#                     <div class="stat-label">Total Receipts</div>
#                     <div class="stat-value">{total_receipts}</div>
#                 </div>
#                 <div class="stat-card">
#                     <div class="stat-label">Total Revenue</div>
#                     <div class="stat-value">฿{total_revenue:,.2f}</div>
#                 </div>
#                 <div class="stat-card">
#                     <div class="stat-label">Avg per Receipt</div>
#                     <div class="stat-value">฿{(total_revenue/total_receipts if total_receipts > 0 else 0):,.2f}</div>
#                 </div>
#             </div>
#         </div>
#         <div class="footer">
#             <p>This is an automated message from BKK Print Service.<br>
#             Please do not reply to this email.</p>
#         </div>
#     </div>
# </body>
# </html>
#         """
        
#         return self.send_email(to_emails, subject, html_content, text_content)