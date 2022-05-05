from tkinter import *
import smtplib

from sympy import expand

#Main Screen
root = Tk()
root.title('Custom Python Email App')
root.geometry("250x300")

#functions
def send():
    print("Send")

def reset():
    print("reset")
    
#SMTP or SOCKET

Radiobutton(root, text="SMTP", variable=2, value=1).grid(row=2, column=0, sticky=W)
Label(root, text="Port:", font=('Calibri', 11)).grid(row=2, column=1, sticky=W)
Radiobutton(root, text="TCP/Socket", variable=2, value=2).grid(row=2, column=3, sticky=W)

#Graphics
Label(root, text="Custom Email App", font=('Calibri', 15)).grid(row=0, sticky=N)
Label(root, text="Use the form below to send an email", font=('Calibri', 11)).grid(row=1, sticky=W, padx=8)

Label(root, text="Email:", font=('Calibri', 11)).grid(row=3, sticky=W, padx=8)
Label(root, text="Password:", font=('Calibri', 11)).grid(row=4, sticky=W, padx=8)
Label(root, text="To:", font=('Calibri', 11)).grid(row=5, sticky=W, padx=8)
Label(root, text="Subject:", font=('Calibri', 11)).grid(row=6, sticky=W, padx=8)
Label(root, text="Body", font=('Calibri', 11)).grid(row=7, sticky=W, padx=8)

notif = Label(root, text="", font=('Calibri', 11)).grid(row=8, sticky=S, padx=8)

#Storage
temp_port = StringVar()
temp_username = StringVar()
temp_password = StringVar()
temp_receiver = StringVar()
temp_subject = StringVar()
temp_body = StringVar()

#Entries
portEntry = Entry(root, textvariable = temp_port)
portEntry.grid(row=2, column=2)

usernameEntry = Entry(root, textvariable = temp_username)
usernameEntry.grid(row=3, column=0)

passwordEntry = Entry(root, show="*", textvariable = temp_password)
passwordEntry.grid(row=4, column=0)

receiverEntry = Entry(root, textvariable = temp_receiver)
receiverEntry.grid(row=5, column=0)

subjectEntry = Entry(root, textvariable = temp_subject)
subjectEntry.grid(row=6, column=0)

subjectBody = Entry(root, textvariable = temp_body)
subjectBody.grid(row=7, column=0)

#Buttons
Button(root, text="Send", command=send).grid(row=8, sticky=W, pady=15, padx=8)
Button(root, text="Reset", command=reset).grid(row=8, sticky=W, pady=45, padx=45)

root.mainloop()