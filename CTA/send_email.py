"""
email is sent using a third part email address, I haven't tried using our public email "noc@ctamercas.com" yet.
the impact device and interface is included in the email body therefore engineers will be noted of the detail
"""
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class MAIL_SENDER:
    def __init__(self, usermail, password, obj_address, obj_address_cc, smtpserver, smtpport=25):
        self.usermail = usermail
        self.password = password
        self.obj_address = obj_address
        self.obj_address_cc = obj_address_cc
        self.smtpserver = smtpserver
        self.smtpport = smtpport

    def create_mail(self, subject, content):
        msg = MIMEMultipart('mixed')
        msg['From'] = self.usermail
        msg['To'] = self.obj_address
        msg['Cc'] = self.obj_address_cc
        msg['Subject'] = Header(subject, 'utf-8')
        text_sub = MIMEText(content, 'plain', 'utf-8')
        msg.attach(text_sub)
        return msg.as_string()

    def send(self, msg):
        try:
            sender = smtplib.SMTP(self.smtpserver, self.smtpport)
            sender.login(self.usermail, self.password)
            sender.sendmail(self.usermail, self.obj_address.split(',') + self.obj_address_cc.split(','), msg)
            print("Email Sent Successfully")
            sender.quit()
        except Exception as e:
            print("Failed to Send Email, Error as Follow: ")
            print(e)


def send_email(subject, content):
    reporter = MAIL_SENDER("CT_notifier@tom.com", "Cta8889+1", "yuchili@ctamericas.com", "", "smtp.tom.com")
    msg = reporter.create_mail(subject, content)
    reporter.send(msg)
