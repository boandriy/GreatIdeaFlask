#!/usr/bin/python
#
# aba - ext IP change notifier
#
from urllib import urlopen
import re
import smtplib
import syslog
import requests

FROM = "pi.raspberry.ab@gmail.com"
MAILPASS = "pi2383350"
MAILSERVER = "smtp.gmail.com:587"
TO = "ab@ucu.edu.ua"
EXTIPHOLDER = "/opt/ipchecker/externalIP.txt"

# function to grab ip address
def getPublicIp():
    data = str(urlopen('http://checkip.dyndns.com/').read())
    ipObj = re.compile(r'\d+\.\d+\.\d+\.\d+')
    ip = ipObj.search(data)
    return(ip.group())

def save_IP(ip):
    file = open(EXTIPHOLDER,"w")
    file.write(ip)
    file.close

def read_saved_IP():
    try:
        file = open(EXTIPHOLDER,"r")
    except:
        return "No file"
    ip = file.readline()
    file.close
    return ip

def send_email(fromaddr,toaddrs,msg):
    server = smtplib.SMTP(MAILSERVER)
    server.starttls()
    server.login(FROM,MAILPASS)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()
    
#
#main:
#
msg_template="""From: {}
To: {}
Subject: IP address changed ({})

RPI external IP changed to {} (was:{})
Dynamic DNS at now-ip.com (ab.mypi.co) updated accordingly"""

new_ip = getPublicIp().strip("\n")
old_ip = read_saved_IP().strip("\n")

if new_ip == old_ip:
    pass
    # print("IP Address not changed({})".format(str(ip)))
else:
    log = syslog.syslog
    try:
        from settingsabababab import USERNAME, PASSWORD, HOSTNAME
    except:
        HOSTNAME = "ab.mypi.co"                 # now-ip.com hostname
        USERNAME = "andriyborovets@gmail.com"   # now-ip.com username
        PASSWORD = "ab@lvivnet.com"             # now-ip.com password

#    _new_ = urllib2.urlopen("http://api.enlightns.com/tools/whatismyip/?format=text").read().strip()
    _url_ = "https://now-ip.com/update?hostname={hostname}&myip={ip}"

    log('ipchecker: Update www.now-ip.com account: OLD IP: {}, NEW IP: {}'.format(old_ip, new_ip))

    # Update current now-ip.com DDNS
    print("updating DDNS @ mow-ip.com: login={},pass={}".format(USERNAME, PASSWORD))
    _url_called_ = _url_.format(hostname=HOSTNAME, ip=new_ip)
    r = requests.get(_url_called_, auth=(USERNAME, PASSWORD))
    print r.status_code  # if 200 this means the page was reached
    print r.content      # should be the response from noip.com

    if r.status_code == 200:
        success = 'yes'
    else:
        success = 'no'

    log('ipchecker: Succeed: {success}'.format(success=success))


    msg = msg_template.format (FROM, TO, str(new_ip), str(new_ip),str(old_ip))
    send_email(FROM,TO,msg)
    save_IP(new_ip)
    print("New IP address: {}".format(new_ip))

