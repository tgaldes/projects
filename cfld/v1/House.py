from interface import implements
from Interfaces import IAddressee

class House(implements(IAddressee)):
    def __init__(self, named_tuple):
        self.data = named_tuple
    def send_mail(self, letter_sender):
        sender.send_mail('An address', 'This is a letter for {}'.format(self.name))
