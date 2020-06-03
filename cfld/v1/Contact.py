from IAddressee import IAddressee

class Contact(IAddressee):
    def __init__(self, named_tuple):
        self.data = named_tuple
    def write_letter(self):
        return 'This is a letter for {}'.format(self.name)

