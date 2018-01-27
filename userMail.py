from urllib import urlopen
import re
import smtplib
import syslog
import requests
from dbObjects import User


FROM = "some mail"              #replace with actual account info
MAILPASS = "some pass"
MAILSERVER = "smtp.gmail.com:587"



class UserMail():
    def __init__(self,user):
        self.From = FROM
        self.mailpass = MAILPASS
        self.mailserver = MAILSERVER
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

