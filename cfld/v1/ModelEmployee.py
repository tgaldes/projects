from House import House
from Contact import Contact
import collections
from Google import Google
import spreadsheet_constants
import pdb
import pickle

class ModelEmployee:
    def __init__(self, g):
        #self.apiToken = apiToken
        self.google = g
# TODO: verify on creation that (self.data.short_name, self.data.fraternity, self.data.name) in list of contacts creates a unique person, if it doesn't we need to rethink the keys
        HouseData = collections.namedtuple('HouseData', spreadsheet_constants.house_data_header)
        ContactData = collections.namedtuple('ContactData', spreadsheet_constants.contact_data_header)
# maybe we should hold Iaddressees and Iemailaddresses in two lists
        self.houses = []
        self.contacts = []
        for data in g.get_clean_data(spreadsheet_constants.sheet_names['houses'], spreadsheet_constants.ffill_column_names['houses'])[1:]: # skip the header
            self.houses.append(House(HouseData(*(data[:spreadsheet_constants.house_data_header_length]))))
        for data in g.get_clean_data(spreadsheet_constants.sheet_names['contacts'], spreadsheet_constants.ffill_column_names['contacts'])[1:]: # skip the header
            # look up the right house in the list of houses
            lookup_keys = data[:spreadsheet_constants.columns_that_define_unique_house]
            for house in self.houses:
                if lookup_keys == house.data[:spreadsheet_constants.columns_that_define_unique_house]:
                    self.contacts.append(Contact(ContactData(*(data[:spreadsheet_constants.contact_data_header_length - 1]), house.data))) # subtract 1 so we can add the house data named tuple to the contact data
                    break

    def send_intro_emails(self, min_duplicate_days,
                          school_filter=[],
                          school_filter_is_include=True,
                          code_filter=[],
                          code_filter_is_include=True):
        print('sending into emails')
    def make_phone_calls(self, min_duplicate_days,
                          school_filter=[],
                          school_filter_is_include=True,
                          code_filter=[],
                          code_filter_is_include=True):
        print('making phone calls')
    # Note that snail mail can go to contacts AND houses, which will have different sets of codes
    def send_snail_mail(self, min_duplicate_days,
                          school_filter=[],
                          school_filter_is_include=True,
                          house_code_filter=[],
                          house_code_filter_is_include=True,
                          contact_code_filter=[],
                          contact_code_filter_is_include=True):
        '''for house in self.houses:
            print(house.write_letter())'''
        for contact in self.contacts:
            contact.send_mail(self.g)
    def get_school_list(self):
        return ['UCLA', 'USC', 'Denver', 'Georgia Tech']
    def get_house_code_list(self):
        return ['active', 'suspended']
    def get_contact_code_list(self): 
        return ['agent', 'board', 'general_board', 'undergrad', 'contact']




if __name__=='__main__':
    g2 = Google()
    emp = ModelEmployee(g2)
    emp.send_snail_mail(365, 'USC')


