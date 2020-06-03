from House import House
from Contact import Contact
import collections
from Google import Google
import spreadsheet_constants
import pdb

class ModelEmployee:
    def __init__(self, g):
        #self.apiToken = apiToken
        self.google = g
        HouseData = collections.namedtuple('HouseData', g.get_header(spreadsheet_constants.sheet_names['houses']))
        ContactData = collections.namedtuple('ContactData', g.get_header(spreadsheet_constants.sheet_names['contacts']))
# maybe we should hold Iaddressees and Iemailaddresses in two lists
        self.houses = []
        self.contacts = []
        for data in g.get_clean_data(spreadsheet_constants.sheet_names['houses'], spreadsheet_constants.ffill_column_names['houses'])[1:]:
            self.houses.append(House(HouseData(*data)))
        for data in g.get_clean_data(spreadsheet_constants.sheet_names['contacts'], spreadsheet_constants.ffill_column_names['contacts'])[1:]:
            self.contacts.append(Contact(ContactData(*data)))
        pdb.set_trace()

    def send_intro_emails(self, min_duplicate_days,
                          house_filter=[],
                          house_filter_is_include=True,
                          school_filter=[],
                          school_filter_is_include=True,
                          code_filter=[],
                          code_filter_is_include=True):
        pass
    def make_phone_calls(self, min_duplicate_days,
                          house_filter=[],
                          house_filter_is_include=True,
                          school_filter=[],
                          school_filter_is_include=True,
                          code_filter=[],
                          code_filter_is_include=True):
        pass
    def send_snail_mail(self, min_duplicate_days,
                          house_filter=[],
                          house_filter_is_include=True,
                          school_filter=[],
                          school_filter_is_include=True,
                          code_filter=[],
                          code_filter_is_include=True):
        for house in self.houses:
            print(house.write_letter())





if __name__=='__main__':
    g = Google()
    emp = ModelEmployee(g)
    #emp.send_snail_mail(365)


