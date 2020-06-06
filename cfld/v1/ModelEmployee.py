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
        '''HouseData = collections.namedtuple('HouseData', g.get_header(spreadsheet_constants.sheet_names['houses']))
        ContactData = collections.namedtuple('ContactData', g.get_header(spreadsheet_constants.sheet_names['contacts']))
# maybe we should hold Iaddressees and Iemailaddresses in two lists
        self.houses = []
        self.contacts = []
        for data in g.get_clean_data(spreadsheet_constants.sheet_names['houses'], spreadsheet_constants.ffill_column_names['houses'])[1:]:
            self.houses.append(House(HouseData(*data)))
        for data in g.get_clean_data(spreadsheet_constants.sheet_names['contacts'], spreadsheet_constants.ffill_column_names['contacts'])[1:]:
            self.contacts.append(Contact(ContactData(*data)))'''

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
        for house in self.houses:
            print(house.write_letter())
        print('writing letters')
    def get_school_list(self):
        return ['UCLA', 'USC', 'Denver', 'Georgia Tech']
    def get_house_code_list(self):
        return ['active', 'suspended']
    def get_contact_code_list(self): 
        return ['agent', 'board', 'general_board', 'undergrad', 'contact']




if __name__=='__main__':
    with open('pickles/google.pickle', 'rb') as f:
        g2 = pickle.load(f)
    emp = ModelEmployee(g2)
    #emp.send_snail_mail(365)


