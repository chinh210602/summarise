from email.message import EmailMessage
import ssl
import smtplib

class EmailSender():
    def __init__(self):
        pass
    
    def send(self, sender, receivers, password, subject, body):
        em = EmailMessage()
        em['From'] = sender
        em['To'] = receivers
        em['Subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(sender, password)
            smtp.sendmail(sender, receivers, em.as_string())
        