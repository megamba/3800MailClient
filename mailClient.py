from distutils.command import clean
import email
import imaplib
from nntplib import decode_header
import os
from ssl import Options
import webbrowser
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, uic
import sys

import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

class MyGUI(QMainWindow):
    def __init__(self, parent=None):
        super(MyGUI, self).__init__()
        uic.loadUi("MailClient.ui", self)
        self.show()
        
        self.loginButton.clicked.connect(self.login)
        self.attachButton.clicked.connect(self.attach)
        self.sendButton.clicked.connect(self.sendMail)
        self.inboxButton.clicked.connect(self.openInbox)
        
        self.dialog = InboxGUI(self)
        
    # Login using SMTP server given and Port number
    def login(self):
        try:
            self.server = smtplib.SMTP(self.SMTPEdit.text(), self.portEdit.text())
            
            # HANDSHAKING
            # make connection with server and start TLS(encryption), ensure connection was made
            self.server.ehlo()
            self.server.starttls()
            self.server.ehlo()
            self.server.login(self.emailEdit.text(), self.passwordEdit.text())
            
            #disable login credential fields
            self.emailEdit.setEnabled(False)
            self.passwordEdit.setEnabled(False)
            self.SMTPEdit.setEnabled(False)
            self.portEdit.setEnabled(False)
            self.loginButton.setEnabled(False)
            
            #enable sending fields
            self.toEdit.setEnabled(True)
            self.subjectEdit.setEnabled(True)
            self.messageEdit.setEnabled(True)
            self.attachButton.setEnabled(True)
            self.sendButton.setEnabled(True)
            self.inboxButton.setEnabled(True)
            
            self.msg = MIMEMultipart()
        except smtplib.SMTPAuthenticationError:
            message_box = QMessageBox()
            message_box.setText('Invalid Login Info')
            message_box.exec()
        except:
            message_box = QMessageBox()
            message_box.setText('Login Failed')
            message_box.exec()
            
    def attach(self):
        options = QFileDialog.Options()
        filenames, _ = QFileDialog.getOpenFileNames(self, "Open File", "", "All Files (*.*)", options = options)
        if filenames != []:
            for filename in filenames:
                attachment = open(filename, 'rb')
                
                filename = filename[filename.rfind("/") + 1:]
                
                payload = MIMEBase('application','octet-stream')
                payload.set_payload(attachment.read())
                encoders.encode_base64(payload)
                payload.add_header("Content-Disposition", f"attachment; filename={filename}")
                self.msg.attach(payload)
                
                if not self.attachLabel.text().endswith(": "):
                    self.attachLabel.setText(self.attachLabel.text() + ",")
                self.attachLabel.setText(self.attachLabel.text() + " " + filename)
                
    def sendMail(self):
        #Send Confirmation prompt
        dialog = QMessageBox()
        dialog.setText('Do you want to send this mail?')
        dialog.addButton(QPushButton("Yes"), QMessageBox.YesRole)
        dialog.addButton(QPushButton("No"), QMessageBox.NoRole)
        
        if dialog.exec_() == 0:
            try:
                self.msg['From'] = "CPP Test Mail"
                self.msg['To'] = self.toEdit.text()
                self.msg['Subject'] = self.subjectEdit.text()
                self.msg.attach(MIMEText(self.messageEdit.toPlainText(),'plain'))
                text = self.msg.as_string()
                self.server.sendmail(self.emailEdit.text(), self.toEdit.text(), text)
                #Inform User of Sent Mail
                message_box = QMessageBox()
                message_box.setText('Mail Sent')
                message_box.exec()
                
                #this needs work..
                # self.toEdit.setText('')
                # self.subjectEdit.setText('')
                # self.messageEdit.setText('')
                # self.attachLabel.setText('Attachments: ')
            except:
                message_box = QMessageBox()
                message_box.setText('Sending Mail Failed')
                message_box.exec()
    
    def openInbox(self):
        self.dialog.show()

class InboxGUI(QMainWindow):
    def __init__(self, parent=None):
        super(InboxGUI, self).__init__()
        uic.loadUi("InboxUI.ui", self)
        
        self.pushButton.clicked.connect(self.showInbox)
        
    def showInbox(self):
        # create an IMAP4 class with SSL 
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        # authenticate
        imap.login("cpp.cs.testmail@gmail.com", "broncoTesting1!")
        
        status, messages = imap.select("INBOX")
        # number of top emails to fetch
        N = 3
        # total number of emails
        messages = int(messages[0])
        for i in range(messages, messages-N, -1):
            # fetch the email message by ID
            res, msg = imap.fetch(str(i), "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    # parse a bytes email into a message object
                    msg = email.message_from_bytes(response[1])
                    # decode the email subject
                    subject, encoding = decode_header(msg["Subject"]),[0]
                    if isinstance(subject, bytes):
                        # if it's a bytes, decode to str
                        subject = subject.decode(encoding)
                    # decode email sender
                    From, encoding = decode_header(msg.get("From"))[0]
                    if isinstance(From, bytes):
                        From = From.decode(encoding)
                    print("Subject:", subject)
                    print("From:", From)
                    # if the email message is multipart
                    if msg.is_multipart():
                        # iterate over email parts
                        for part in msg.walk():
                            # extract content type of email
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            try:
                                # get the email body
                                body = part.get_payload(decode=True).decode()
                            except:
                                pass
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                # print text/plain emails and skip attachments
                                print(body)
                            elif "attachment" in content_disposition:
                                # download attachment
                                filename = part.get_filename()
                                if filename:
                                    folder_name = clean(subject)
                                    if not os.path.isdir(folder_name):
                                        # make a folder for this email (named after the subject)
                                        os.mkdir(folder_name)
                                    filepath = os.path.join(folder_name, filename)
                                    # download attachment and save it
                                    open(filepath, "wb").write(part.get_payload(decode=True))
                    else:
                        # extract content type of email
                        content_type = msg.get_content_type()
                        # get the email body
                        body = msg.get_payload(decode=True).decode()
                        if content_type == "text/plain":
                            # print only text email parts
                            print(body)
                    if content_type == "text/html":
                        # if it's HTML, create a new HTML file and open it in browser
                        folder_name = clean(subject)
                        if not os.path.isdir(folder_name):
                            # make a folder for this email (named after the subject)
                            os.mkdir(folder_name)
                        filename = "index.html"
                        filepath = os.path.join(folder_name, filename)
                        # write the file
                        open(filepath, "w").write(body)
                        # open in the default browser
                        webbrowser.open(filepath)
                    print("="*100)
        # close the connection and logout
        imap.close()
        imap.logout()


app = QtWidgets.QApplication(sys.argv)
window = MyGUI()
sys.exit(app.exec_())

