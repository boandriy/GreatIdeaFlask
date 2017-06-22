from urllib import urlopen
import re
import smtplib
import syslog
import requests
from dbObjects import User


FROM = "pi.raspberry.ab@gmail.com"
MAILPASS = "pi2383350"
MAILSERVER = "smtp.gmail.com:587"



class UserMail():
    def __init__(self,user):
        self.From = "pi.raspberry.ab@gmail.com"
        self.mailpass = "pi2383350"
        self.mailserver = "smtp.gmail.com:587"
        self.user = user


    def send_signup(self):
        msg_template = """From: {}
To: {}
Subject: validation pin

Your pin is: {}
"""
        msg = msg_template.format(self.From, self.user.email, self.user.pin)
        server = smtplib.SMTP(self.mailserver)
        server.starttls()
        server.login(self.From,self.mailpass)
        server.sendmail(self.From,self.user.email,msg)
        server.quit()



    def send_reset_pass(self):
        pass

