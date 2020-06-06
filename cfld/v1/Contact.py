from interface import implements
from Interfaces import IAddressee, IEmailAddressee

class Contact(implements(IAddressee), implements(IEmailAddressee)):
    def __init__(self, named_tuple):
        self.data = named_tuple
    def send_mail(self, letter_sender):
        sender.send_mail('An address', 'This is a letter for {}'.format(self.name))
    def send_email(self, email_sender):
        email_sender.send_mail('A subject', 'This is a letter for {}'.format(self.name), 'tgaldes@gmail.com')

