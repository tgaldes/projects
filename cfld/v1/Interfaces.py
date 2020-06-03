from interface import Interface

class IAddressee:
    def write_letter() -> str:
        pass

class IEmailAddressee:
    def send_mail() -> str:
        pass

class IEmailSender(Interface):
    def send_mail(self, subject, msg, to_addr=''):
        pass

class ILetterSender(Interface):
    def send_mail(self, address, msg):
        pass




