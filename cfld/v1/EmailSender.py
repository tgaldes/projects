import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from interface import implements
from Interfaces import IEmailSender

def get_password():
    with open('/home/tgaldes/Dropbox/Fraternity PM/dev_private/app_password', 'r') as f:
        return f.read()

class EmailSender(implements(IEmailSender)):
    def __init__(self, addr='tyler@cleanfloorslockingdoors.com'):
        self.sender_address = addr
        self.password = get_password()
        self.session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        self.session.starttls() #enable security
        #login with mail_id and password
        self.session.login(self.sender_address, self.password) 
        #TEST
        print('TEST: Overwriting all emails to {} for testing purposes.'.format(to_addr))
    def __def__(self):
        self.session.quit()

    def send_mail(self, subject, msg, to_addr='tgaldes@gmail.com'):
        #TEST
        to_addr='tgaldes@gmail.com'

        message = MIMEMultipart()
        message['From'] = self.sender_address
        message['To'] = to_addr
        message['Subject'] = subject
        message.attach(MIMEText(msg, 'plain'))
        text = message.as_string()
        self.session.sendmail(self.sender_address, to_addr, text)
        print('Sent email to {} with subject: {}'.format(to_addr, subject))

class MockEmailSender(implements(IEmailSender)):
    def __init__(self):
        pass
    def send_mail(self, subject, msg, to_addr='console'):
        print('Sent mock email to {} with subject: {}'.format(to_addr, subject))

if __name__=='__main__':
    e = EmailSender()
    e.send_mail('Hello from the command line', 'This is the most creative msg body you could come up with?!?')
    e = MockEmailSender()
    e.send_mail('Hello from the command line', 'This is the most creative msg body you could come up with?!?')



