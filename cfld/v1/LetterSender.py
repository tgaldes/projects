from interface import implements
from Interfaces import ILetterSender

class MockLetterSender(implements(ILetterSender)):
    def __init__(self):
        pass
    def send_mail(self, address, msg):
        print('Sent mock letter to address:\n{}'.format(address))




if __name__=='__main__':
    e = MockLetterSender()
    e.send_mail('11500 Tennesee Ave\n#324\nLos Angeles CA 90064', 'Hello from the command line')




