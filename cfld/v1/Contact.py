from interface import implements
from Interfaces import IAddressee, IEmailAddressee
import letters
from global_funcs import safe_get_attr
import enums
import spreadsheet_constants

# Imported for testing, used in main:
#from LetterSender import MockLetterSender
# TODO: fix MockLetterSender interface
import collections
from Google import Google
import pickle
import pdb

class Contact(implements(IAddressee), implements(IEmailAddressee)):
    mail_skip_codes = ['contact', '', 'contact_form', 'skip', 'undergrad_contact_form']
    email_skip_codes = ['contact', '', 'contact_form', 'skip', 'undergrad_contact_form']
    def __init__(self, named_tuple):
        self.data = named_tuple
        self.house_data = named_tuple.house_tuple
        self.datas = [self.data, self.house_data]
        for i in range(spreadsheet_constants.columns_that_define_unique_house):
            l = getattr(self.data, spreadsheet_constants.column_names['contacts'][i])
            r = getattr(self.house_data, spreadsheet_constants.column_names['houses'][i])
            if l != r:
                pdb.set_trace()
                raise Exception('Cannot construct contact with different values {} and {} for {}'.format(l, r, spreadsheet_constants.column_names['contacts'][i]))


    def send_mail(self, letter_sender):
        if self.data.address == '':
            print('Skipping sending mail when address is empty for contact {}, {}, {}'.format(self.data.short_name, self.data.fraternity, self.data.name))
            return
        if self.data.code in Contact.mail_skip_codes:
            print('Skipping sending mail for code: {}'.format(self.data.code))
            return
        if self.data.code not in letters.letters:
            raise Exception('Code: {} is not in letters.py.letters map'.format(self.data.code))
        letter = self.__format_letter()
        letter_sender.send_mail(self.data.address, letter, self.data)

    def send_email(self, email_sender):
        if self.data.email == '':
            print('Skipping sending email when email is empty for contact {}, {}, {}'.format(self.data.short_name, self.data.fraternity, self.data.name))
            return
        if self.data.code in Contact.email_skip_codes:
            print('Skipping sending email for code: {}'.format(self.data.code))
            return
        if self.data.code not in letters.emails:
            raise Exception('Code: {} is not in letters.py.letters map'.format(self.data.code))
        email = self.__format_email()
        email_sender.send_email('TODO: subject', email, self.data)


    def __format_email(self):
        return self.__format_message(enums.MailType.EMAIL)
    def __format_letter(self):
        return self.__format_message(enums.MailType.MAIL)
    def __format_message(self, mail_type_enum):
        if mail_type_enum == enums.MailType.EMAIL:
            m = letters.emails[self.data.code]
        else:
            m = letters.letters[self.data.code]
        return m.format_letter(self.datas)

if __name__=='__main__':
    HouseData = collections.namedtuple('HouseData', spreadsheet_constants.house_data_header)
    ContactData = collections.namedtuple('ContactData', spreadsheet_constants.contact_data_header)
    houses = [HouseData(*x) for x in spreadsheet_constants.house_data_info]
    contacts = [Contact(ContactData(*x, houses[i])) for i, x in enumerate(spreadsheet_constants.contact_data_info)]
    g = Google()
    '''with open('pickles/google.pickle', 'wb') as f:
        pickle.dump(g, f)
    with open('pickles/google.pickle', 'rb') as f:
        g = pickle.load(f)'''
    #b = dch.pad_short_rows(g2.sheets['addresses_clean'])
    #a = dch.ffill(b, ['university', 'fraternity'])
    #print(contacts)
    for c in contacts:
        #c.send_email(g)
        c.send_mail(g)

