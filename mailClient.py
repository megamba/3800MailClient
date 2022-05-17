from distutils.command import clean
import email
import imaplib
from nntplib import decode_header
from operator import mod
import os
from pyexpat import model
from ssl import Options
import ssl
import webbrowser
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, uic
import sys

import base64
from socket import AF_INET, SOCK_STREAM, socket

import smtplib
from email import encoders, message_from_bytes
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

class MyGUI(QMainWindow):

    # init values to use in other functions
    client_socket = None
    hasAttachments = False
    sender = ""

    def __init__(self, parent=None):
        super(MyGUI, self).__init__()
        uic.loadUi("MailClient.ui", self)
        self.show()

        # init socket
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        
        self.loginButton.clicked.connect(self.login)
        self.attachButton.clicked.connect(self.attach)
        self.sendButton.clicked.connect(self.sendMail)
        self.inboxButton.clicked.connect(self.openInbox)
        self.removeButton.clicked.connect(self.remove)
        
        self.dialog = InboxGUI(self)

        self.attachments = []

    # authenticate socket connection
    def authenticate_connection(self, sender, password):
        
        base64Login = base64.b64encode(bytes(sender, 'utf-8'))
        base64Password = base64.b64encode(bytes(password, 'utf-8'))

        # send HELO command and print server response
        hello_command = b'EHLO localhost\r\n'
        self.client_socket.send(hello_command)
        recv = self.client_socket.recv(1024)
        print('helo response: ', recv[:3].decode())

        # send login info
        self.client_socket.send(b'AUTH LOGIN %s\r\n' % base64Login)
        recv = self.client_socket.recv(1024)
        print('auth response: ', recv[:3].decode())

        # send password
        self.client_socket.send(b'%s\r\n' % base64Password)
        recv2 = self.client_socket.recv(1024)
        print('password response: ', recv[:3].decode())
        print('authenticaiton successful')
        
    # Login using SMTP server given and Port number
    def login(self):

        global client_socket
        try:

            sender = self.emailEdit.text()

            # eastblish SSl connection with socket
            try:
                print('trying to wrap socket')
                self.client_socket = ssl.wrap_socket(self.client_socket)
                self.client_socket.connect(('smtp.gmail.com', 465)) # ssl connection

                recv = self.client_socket.recv(1024)
                print('wrap reponse: ', recv[:3].decode())

            except Exception as e:
                print("could not wrap socket")
                print('\n\n' + e + '\n\n')

            print("done wrapping socket")

            # authenticate socket connection
            self.authenticate_connection(self.emailEdit.text(), self.passwordEdit.text())

            # HANDSHAKING
            # make connection with server and start TLS(encryption), ensure connection was made
            self.server = smtplib.SMTP(self.SMTPEdit.text(), self.portEdit.text())
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
    
    # add an attachment
    def attach(self):
        options = QFileDialog.Options()
        filenames, _ = QFileDialog.getOpenFileNames(self, "Open File", "", "All Files (*.*)", options = options)
        if filenames != []:
            for filename in filenames:
                if filename not in self.attachments:
                    self.attachments.append(filename)
                    self.attachList.addItem(filename)
                    self.removeButton.setEnabled(True)

        self.hasAttachments = True

    # remove an attachment
    def remove(self):
        idx = self.attachList.currentRow()
        if idx != -1:
            item = self.attachList.currentItem()
            txt = item.text()
            print(item)
            self.attachList.takeItem(idx)
            self.attachments.remove(txt)
            if self.attachList.count() == 0:
                self.removeButton.setEnabled(False)
                
    def sendMail(self):
        #Send Confirmation prompt
        dialog = QMessageBox()
        dialog.setText('Do you want to send this mail?')
        dialog.addButton(QPushButton("Yes"), QMessageBox.YesRole)
        dialog.addButton(QPushButton("No"), QMessageBox.NoRole)
        
        if dialog.exec_() == 0:
            try:
                
                print('getting message info')
                recipient = str(self.toEdit.text())

                self.msg['From'] = "CPP Test Mail"
                self.msg['To'] = self.toEdit.text()
                self.msg['Subject'] = self.subjectEdit.text()
                self.msg.attach(MIMEText(self.messageEdit.toPlainText(),'plain'))

                # check for attachments 
                if self.hasAttachments:
                    print('message has attachments')
                    text = self.msg.as_string()
                    self.server.sendmail(self.emailEdit.text(), self.toEdit.text(), text)
                else:
                    print('no attachments')

                    # try to send email
                    print('attempting to send email')

                    try: 

                        # authenticate connection
                        self.authenticate_connection(str(self.emailEdit.text()), str(self.passwordEdit.text()))

                        # send MAIL command to server
                        print('encoding sender email now')
                        senderB64 = base64.b64encode(bytes(self.msg['To'], 'utf-8'))
                        self.client_socket.send(b'MAIL FROM: <%s>\r\n' % senderB64)
                        recv = self.client_socket.recv(1024)
                        print('recv of MAIL: ', recv[:3].decode())

                        # send  RCPT command
                        print('sending RCPT command')
                        print('recipient: ', recipient)
                        recipientB64 = base64.b64encode(bytes(recipient, 'utf-8'))
                        #self.client_socket.send(b'RCPT TO: <%s>\r\n' % recipientB64)
                        self.client_socket.send(b'RCPT TO: <%s>\r\n' % bytes(recipient, encoding='utf-8'))
                        recv = self.client_socket.recv(1024)
                        print('rcv of RCPT: ', recv[:3].decode())

                        # send DATA command
                        print('sending DATA command')
                        self.client_socket.send(b'DATA\r\n')
                        recv = self.client_socket.recv(1024)
                        print('recv of DATA: ',recv[:3].decode())

                        # send message data
                        print('sending message data')

                        self.client_socket.send(bytes(self.msg.as_string(), encoding='utf-8'))
                        print('sent encoded message')
                        self.client_socket.send(b'\r\n.\r\n')
                        print('sent message end')
                        recv = self.client_socket.recv(1024)
                        print('recv for data transfer: ', recv[:3].decode())
                    except Exception as e:
                        print(e)

                #Inform User of Sent Mail
                message_box = QMessageBox()
                message_box.setText('Mail Sent')
                message_box.exec()
                
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
        
        self.emails = []
        self.rowCount = 0
        self.rowView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        self.rowView.clicked.connect(self.showEmail)
        
        self.emailView.clear()

        # self.pushButton.clicked.connect(self.print_inbox)
        
    def showInbox(self):
        # clear old emails
        self.rowCount = 0
        self.rowView.setRowCount(0)
        self.emails = {}
        
        # create an IMAP4 class with SSL 
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        # authenticate
        imap.login("cpp.cs.testmail@gmail.com", "broncoTesting1!")
        
        status, messages = imap.select("INBOX")
        # number of top emails to fetch
        N = 10
        # total number of emails
        messages = int(messages[0])
        idx = 0
        for i in range(messages, messages-N, -1):
            # fetch the email message by ID
            try: 
                res, msg = imap.fetch(str(i), "(RFC822)")
            except Exception as e:
                print("\n", e, "\n")
            if res == 'OK':
                for response in msg:
                    if isinstance(response, tuple):
                        # parse a bytes email into a message object
                        msg = email.message_from_bytes(response[1])
                        # decode the email subject
                        subject, encoding = decode_header(msg["Subject"]), [0]
                        if isinstance(subject, bytes):
                            # if it's a bytes, decode to str
                            subject = subject.decode(encoding)
                        # decode email sender
                        From, encoding = decode_header(msg.get("From")), [0]
                        #From = decode_header(msg.get("From"))[0]
                        #encoding = decode_header(msg.get("From"))[1]
                        if isinstance(From, bytes):
                            From = From.decode(encoding)
                        print("Subject:", subject)
                        print("From:", From)
                        print("="*100)
                        
                        rowNum = self.rowCount
                        self.rowCount = self.rowCount + 1
                        self.rowView.setRowCount(self.rowCount)
                        self.rowView.setItem(rowNum,0, QTableWidgetItem(From))
                        self.rowView.setItem(rowNum,1, QTableWidgetItem(subject))
                        
                        body = ""
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
                                    self.emails[idx] = body
            idx = idx + 1
                    
        # close the connection and logout
        imap.close()
        imap.logout()

    # print the inbox to the console
    def print_inbox(self):

        # create an IMAP4 class with SSL 
        imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)

        # authenticate
        imap.login("cpp.cs.testmail@gmail.com", "broncoTesting1!")

        # select the folder to extract from
        imap.select('Inbox')

        # get all emails without searching for a key
        result,  data = imap.uid('search', None, "ALL")

        if result == 'OK':

            # separate mail IDs
            mail_id_list = data[0].split()

            # get message data
            messages = list()
            for i in mail_id_list:
                result, data = imap.uid('fetch', i, '(RFC822)')
                if result == 'OK':
                    messages.append(data)

            # print message data to console
            for msg in messages:
                
                # for each part of the message
                for response_part in msg:
                    
                    # if the current response part is a tuple
                    if type(response_part) is tuple:
                        
                        # print information
                        current_message = message_from_bytes((response_part[1]))

                        print("===========================================")
                        print("From: ", current_message['from'])
                        print("Subject: ", current_message['subject'])
                        print("Body: ")

                        # for  each part in the body
                        for part in current_message.walk():

                            # if the part is plain text, print it
                            if part.get_content_type() == 'text/plain':
                                print(part.get_payload())

        # end imap connection
        imap.close()
        imap.logout()

    def showEmail(self, mi):
            row = mi.row()
            column = mi.column()
            body = self.emails[row]
            print(row)
            print(body)
            self


app = QtWidgets.QApplication(sys.argv)
window = MyGUI()
sys.exit(app.exec_())

