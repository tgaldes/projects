from IAddressee import IAddressee

class House(IAddressee):
    def __init__(self, name):
        self.name = name
    def write_letter(self):
        return 'This is a letter for {}'.format(self.name)
