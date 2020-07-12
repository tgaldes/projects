from interface import implements
from Interfaces import IAddressee, IEmailAddressee
import letters

# Imported for testing, used in main:
from LetterSender import MockLetterSender
import spreadsheet_constants
import collections

class Contact(implements(IAddressee), implements(IEmailAddressee)):
    def __init__(self, named_tuple):
        self.data = named_tuple
        self.house_data = named_tuple.house_tuple
        self.datas = [self.data, self.house_data]
        for i in range(spreadsheet_constants.columns_that_define_unique_house):
            l = getattr(self.data, spreadsheet_constants.column_names['contacts'][i])
            r = getattr(self.house_data, spreadsheet_constants.column_names['houses'][i])
            if l != r:
               raise Exception('Cannot construct contact with different values {} and {} for {}'.format(l, r, spreadsheet_constants.column_names['contacts'][i]))

    def send_mail(self, letter_sender):
        if self.data.address == '':
            print('Skipping sending mail when address is empty for contact {},{},{}'.format(self.data.short_name, self.data.house, self.data.name))
            return
        if self.data.code not in letters.letters:
            raise Exception('Code: {} is not in letters.py.letters map'.format(self.data.code))
        letter = self.__format_letter(letters.letters[self.data.code])
        letter_sender.send_mail(self.data.address, letter)

    def send_email(self, email_sender):
        email_sender.send_mail('A subject', 'This is a letter for {}'.format(self.name), 'tgaldes@gmail.com')


    def __format_letter(self, letter):
        letter_class = letters.letters[self.data.code]
        return letter_class.msg.format(
            *[self.__get_attr(self.datas[x[1]], x[0]) for x in letter_class.fields]) 

    def __get_attr(self, tup, key):
        attr = getattr(tup, key)
        if attr == '':
#           We didn't find what we were looking for, so go through all the NamedTuples until we find a value for the backup key
            if key not in letters.backup_keys:
                raise Exception('Could not find key {} in letters.backup_keys map'.format(key))
            for named_tuple in self.datas:
                attr = getattr(named_tuple, letters.backup_keys[key])
                if attr != '':
                    break
            if attr == '':
                raise Exception('Looking through data tuples for key: {} -> backup_key: {} yielded the empty string. Data tuples: {}'.format(key, letters.backup_keys[key], self.datas))
        return attr


if __name__=='__main__':
    mls = MockLetterSender()
    HouseData = collections.namedtuple('HouseData', spreadsheet_constants.house_data_header)
    ContactData = collections.namedtuple('ContactData', spreadsheet_constants.contact_data_header)
    houses = [HouseData(*x) for x in spreadsheet_constants.house_data_info]
    contacts = [Contact(ContactData(*x, houses[i])) for i, x in enumerate(spreadsheet_constants.contact_data_info)]
    print(contacts)
    for c in contacts:
        c.send_mail(mls)
        print(getattr(c.data, 'name'))



