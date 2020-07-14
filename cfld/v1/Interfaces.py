from interface import Interface

class IAddressee(Interface):
    def send_mail(self, letter_sender):
        pass

class IEmailAddressee(Interface):
    def send_email(self, email_sender):
        pass

class IEmailSender(Interface):
    def send_mail(self, subject, msg, to_addr=''):
        pass

class ILetterSender(Interface):
    def send_mail(self, address, msg, contact_info):
        pass




