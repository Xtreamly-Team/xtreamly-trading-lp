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

def _send_user_email(email_receiver, df_opn, df_cls):
    subj = f"[Copytrading Action Required] Open & Close Position in Uniswap"
    html_table_opn = df_opn.to_html(index=False, border=0, justify="center", classes="dataframe", escape=False)
    html_table_cls = df_cls.to_html(index=False, border=0, justify="center", classes="dataframe", escape=False)

    html_body = f"""
<html>
  <head>
    <style>
      table.dataframe {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
        font-size: 8px; /* <-- Smaller font */
      }}
      table.dataframe th, table.dataframe td {{
        border: 1px solid #ccc;
        padding: 6px; /* Slightly smaller padding too */
        text-align: center;
      }}
      table.dataframe th {{
        background-color: #f5f5f5;
      }}
    </style>
  </head>
  <body style="font-family: Arial, sans-serif; line-height: 1.5; background-color: #fff; padding: 10px;">
    <p>Open positions (if not opened):</p>
    {html_table_opn}
    <p>Close positions (if opened):</p>
    {html_table_cls}
    <p style="margin-top: 20px;">
      <a href="https://app.uniswap.org/positions/create" 
         style="text-decoration: none; padding: 10px 15px; border-radius: 8px; font-weight: 600; color: white; background: linear-gradient(to top right, #be185d, #db2777, #ec4899); display: inline-block;">
         🦄 Go to Uniswap
      </a>
    </p>
    <p style="margin-top: 20px;">❤ Xtreamly Team</p>
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
# email_receiver_list = ['pablo.masior@gmail.com', 'p.masior@gmail.com']
# _send_user_email(email_receiver_list, df_opn, df_cls)
# =============================================================================

    
