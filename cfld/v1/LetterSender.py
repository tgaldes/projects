from interface import implements
from Interfaces import ILetterSender

# TODO: can we just make the Google class an ILetterSender?
class MockLetterSender(implements(ILetterSender)):
    def __init__(self):
    # TODO: give our letter sender access to Google and
    # expose calls to:
        # 1- append our message to the google sheet containing one page letters
        # 2- make a note in the contacts sheet in pnc doc saying the date that we mailed the letter
        pass
    def send_mail(self, address, msg):
        print('Sending: "{}"\nAddress:\n{}'.format(msg, address))
# TODO: use calls 1 and 2 above




if __name__=='__main__':
    e = MockLetterSender()
    e.send_mail('11500 Tennesee Ave\n#324\nLos Angeles CA 90064', 'Hello from the command line')




