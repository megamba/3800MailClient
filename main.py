from email.mime.base import MIMEBase
import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#define SMTP server going to be used -> Gmail
server = smtplib.SMTP('smtp.gmail.com',25)

#start process, identify as local host to SMTP server
server.ehlo()
server.starttls()
server.ehlo()

#login to sender email
with open('password.txt', 'r') as f:
    password = f.read()
    
server.login('cpp.cs.testmail@gmail.com', password)

msg = MIMEMultipart()
msg['From'] = 'Imaginary Sender'
msg['To'] = 'Mikelly'
msg['Subject'] = 'this is the subject'

with open('message.txt', 'r') as f:
    message = f.read()
    
msg.attach(MIMEText(message, 'plain'))

#attaching an image to the email
filename = 'desk.jpg'
attachment = open(filename, 'rb')

payload = MIMEBase('application', 'octet-stream')
payload.set_payload(attachment.read())

encoders.encode_base64(payload)
payload.add_header('Content-Disposition', f'attachment; filename={filename}')

msg.attach(payload)

text = msg.as_string()
server.sendmail('cpp.cs.testmail@gmail.com', 'michelle.gamba@hotmail.com', text)