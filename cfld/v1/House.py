from interface import implements
from Interfaces import IAddressee

# TODO: House should inherit from Contact so we can override some function calls and behavior but still take advantage of the IAddressee implemented in Contact
# TODO: House won't have an email address, but not all contacts will be created with a populated email address string, so we'll have to support a Contact instance being an 'IEmailAddressee' even if we don't have an email address
class House(implements(IAddressee)):
    def __init__(self, named_tuple):
        self.data = named_tuple
    def send_mail(self, letter_sender):
        sender.send_mail('An address', 'This is a letter for {}'.format(self.name))
