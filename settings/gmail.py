import os
from email.message import EmailMessage
import ssl
import smtplib
import base64
import email.message
from email.message import EmailMessage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
# import requests
from io import BytesIO
from dotenv import load_dotenv
load_dotenv()

email_sender = "info@dalongo.com"
email_pwd = os.environ['GMAIL_KEY'].replace('_', ' ')
email_receiver = "pablo.masior@gmail.com"

def _send_mail(user, Input, pdf):
    email_receiver = user['email']
    say_hi = f"Hello {user['name']}" if 'name' in user else 'Hello'
    period = 'f'+Input['period'][1:]
    dest = Input["name_city"].split(',')[0]

    subj = f"Your Dalongo Guidebook [{Input['name_city']}]"
    html_body = f"""
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.5; background-color: #fff; padding: 8px;">
    <p>{say_hi} 👋,</p>
    <p style="padding: 2px 0px">Here is your Guidebook for <b>{dest} {period}</b>.</p>
    <p style="padding: 10px 0px">Enjoy every moment, wherever you go! 🎉</p>
    <p>✨ Dalongo Team</p>
    <p>ps: We'll ask you for feedback later :)</p>
  </body>
</html>
"""
    em = EmailMessage()
    em['From'] = email_sender
    em["To"] = email_receiver
    em["Subject"] = subj
    em.set_content("Please view this email in HTML format to see the feedback link and image.")
    em.add_alternative(html_body, subtype='html')
    
    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer)
    pdf_data = pdf_buffer.getvalue()
    pdf_buffer.close()
    em.add_attachment(pdf_data, maintype="application", subtype="pdf", filename=f"{subj}.pdf")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(email_sender, email_pwd)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
    return f"Success: sent email from {email_sender}"

def _send_feedback(email_receiver, feedback):
    try:
        em = EmailMessage()
        em['From'] = email_sender
        em["To"] = email_receiver
        em["Subject"] = f"[Feedback] Dalongo"
        em.set_content(f"""{feedback}""")

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(email_sender, email_pwd)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
        return f"Success: sent email from {email_sender}"
    except: pass

def _send_guidebook_request_mail(email, confirmation_link):
    email_receiver = email
    subj = f"Dalongo: Confirm Your Email [{email}]"
    html_body = f"""
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.5; background-color: #fff; padding: 8px;">
    <p style="padding: 2px 0px">Please confirm your email to generate your guidebook:</p>
    <p>
      <a href="{confirmation_link}" 
         style="text-decoration: none; padding: 8px 10px; border-radius: 8px; font-weight: 600; color: white; background: linear-gradient(to top right, #1e40af, #2563eb, #3b82f6); display: inline-block;">
         👍 Confirm my email: {email}
      </a>
    </p>
    <p style="padding: 10px 0px; font-weight: 600">We aim to deliver you the best content. 🏅</p>
    <p>⭐ Dalongo Team</p>
  </body>
</html>
"""
    em = EmailMessage()
    em['From'] = email_sender
    em["To"] = email_receiver
    em["Subject"] = subj
    em.set_content("Please view this email in HTML format to see the feedback link and image.")
    em.add_alternative(html_body, subtype='html')
    
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(email_sender, email_pwd)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
    return f"Success: sent email from {email_sender}"

def _send_user_created_mail(email_receiver, password):
    subj = f"Your Dalongo Account [{email_receiver}]"
    html_body = f"""
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.5; background-color: #fff; padding: 8px;">
    <p style="padding: 2px 0px">Here are your Dalongo Account Credentials:</p>
    <p>✉ Your Login Email: {email_receiver}</p>
    <p>🔐 Password:</p>
    <a
         style="text-decoration: none; padding: 5px 10px; border-radius: 5px; font-weight: 600; color: black; background: linear-gradient(to top right, #f5f5f4, #fafaf9, #ffffff); display: inline-block; border: 2px solid #1c1917;">
         {password}
    </a>
    <p style="padding: 10px 0px; font-weight: 600">We protect your account with maximum security. 🕸️</p>
    <p>💡 Dalongo Team</p>
  </body>
</html>
"""
    em = EmailMessage()
    em['From'] = email_sender
    em["To"] = email_receiver
    em["Subject"] = subj
    em.set_content("Please view this email in HTML format to see the feedback link and image.")
    em.add_alternative(html_body, subtype='html')
    
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(email_sender, email_pwd)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
    return f"Success: sent email from {email_sender}"

def _send_user_email(email_receiver, dest):
    subj = f"We’d love your feedback! [{dest} Guidebook]"
    html_body = f"""
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.0; background-color: #fff; padding: 10px;">
    <p>Hey there 👋</p>
    <p>Got 10 seconds? Tell us how we can improve for you:</p>
    <p>
      <a href="https://dalongo.com/feedback" 
         style="text-decoration: none; padding: 8px 10px; border-radius: 8px; font-weight: 600; color: white; background: linear-gradient(to top right, #1e40af, #2563eb, #3b82f6); display: inline-block;">
         🕊️ Share Your Feedback
      </a>
    </p>
    <p style="padding: 0px 0px; font-weight: 600">Thank you - we really appreciate it!</p>
    <p>❤ Dalongo Team</p>
  </body>
</html>
    """
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subj
    em.set_content("Please view this email in HTML format to see the feedback link and image.")
    em.add_alternative(html_body, subtype='html')

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(email_sender, email_pwd)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

    return f"✅ Success: Email sent to {email_receiver}"

# =============================================================================
# # Usage
# dest = "Wroclaw"
# email_receiver = "pablo.masior@gmail.com"
# _send_user_email(email_receiver, dest)
# =============================================================================

# =============================================================================
#     fp = open(os.path.join('emojis', 'favicon.png'), 'rb')
#     image_favicon = MIMEImage(fp.read())
#     image_favicon.add_header('Content-ID', '<favicon>')
#     fp.close()  
# 
#     fp = open(os.path.join('emojis', 'dove.png'), 'rb')
#     image_dove = MIMEImage(fp.read())
#     image_dove.add_header('Content-ID', '<dove>')
#     fp.close() 
#     
#     em.attach(image_dove)
# =============================================================================
