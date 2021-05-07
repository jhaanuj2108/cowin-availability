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
        gmail_user = os.getenv('gmail_user')
        gmail_password = os.getenv('gmail_password')
        sent_from = gmail_user
        subject = 'Cowin Slots Availability at your area'
        body = "Hey, we found some slots at your area, check it out before it goes away. \n\nHospital Detail: " + self.index + "\nSlots: " + str(self.slots) + "\nAge: " + str(self.age) + "\nDate: " + self.date
        # email_text = """
        # Subject: {0}
        # {1}
        # """.format(subject, body)
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = sent_from
        msg['To'] = to

        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(gmail_user, gmail_password)
            server.send_message(msg)
            server.quit()

            # server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            # server.ehlo()
            # server.login(gmail_user, gmail_password)
            # server.sendmail(sent_from, self.to, email_text)
            # server.close()

            print(f"Email sent to {self.to}")
        except:
            print('Something went wrong...')





