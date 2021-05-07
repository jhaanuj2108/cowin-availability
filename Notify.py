import smtplib
import os
from email.message import EmailMessage

class Notify:
    def __init__(self, to, index, slots, age, date):
        self.to = to
        self.index = index
        self.slots = slots
        self.age = age
        self.date = date


    def send_mail(self):
        gmail_user = os.getenv('gmail_user')
        gmail_password = os.getenv('gmail_password')
        sent_from = gmail_user
        subject = 'Cowin Slots Availability at your area'
        body = "Hey, we found some slots at your area, check it out before it goes away. \n\nHospital Detail: " + self.index + "\nSlots: " + str(self.slots) + "\nAge: " + str(self.age) + "\nDate: " + self.date
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = sent_from
        msg['To'] = self.to

        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(gmail_user, gmail_password)
            server.send_message(msg)
            server.quit()
            print(f"Email sent to {self.to}")
            return True
        except:
            print('Could not send email to', self.to)
            return False





