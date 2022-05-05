from ssl import Options
from PyQt5.QtWidgets import *
from PyQt5 import uic

import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

class MyGUI(QMainWindow):
    def __init__(self):
        super(MyGUI, self).__init__()
        uic.loadUi("MailClient.ui", self)
        self.show()
        
        self.loginButton.clicked.connect(self.login)
        self.attachButton.clicked.connect(self.attach)
        self.sendButton.clicked.connect(self.sendMail)
        
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
        
app = QApplication([])
window = MyGUI()
app.exec_()