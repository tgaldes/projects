from House import House
from Contact import Contact
import collections
from Google import Google
import spreadsheet_constants
import pdb
import pickle
import datetime
from enums import MailType
import datetime
from global_funcs import parse_redirect_log
from UI import UI

class ModelEmployee(UI):
    def __init__(self, g):
        UI.__init__(self)
        #self.apiToken = apiToken
        self.google = g
# TODO: verify on creation that (self.data.short_name, self.data.fraternity, self.data.name) in list of contacts creates a unique person, if it doesn't we need to rethink the keys
        HouseData = collections.namedtuple('HouseData', spreadsheet_constants.house_data_header)
        ContactData = collections.namedtuple('ContactData', spreadsheet_constants.contact_data_header)
        print('Using the following namedtuple class for house data:')
        print(HouseData._fields)
        print('Using the following namedtuple class for contact data:')
        print(ContactData._fields)
# maybe we should hold Iaddressees and Iemailaddresses in two lists
        self.houses = []
        self.contacts = []
        for data in g.get_clean_data(spreadsheet_constants.sheet_names['houses'], spreadsheet_constants.ffill_column_names['houses'])[1:]: # skip the header
            self.houses.append(House(HouseData(*(data[:spreadsheet_constants.house_data_header_length]))))
        for data in g.get_clean_data(spreadsheet_constants.sheet_names['contacts'], spreadsheet_constants.ffill_column_names['contacts'])[1:]: # skip the header
            # look up the right house in the list of houses
            lookup_tuple = tuple(data[:spreadsheet_constants.columns_that_define_unique_house])
            for house in self.houses:
                if lookup_tuple == house.data[:spreadsheet_constants.columns_that_define_unique_house]:
                    self.contacts.append(Contact(ContactData(*(data[:spreadsheet_constants.contact_data_header_length - 1]), house.data))) # subtract 1 so we can add the house data named tuple to the contact data
                    break

        print('Loaded {} houses and {} people'.format(len(self.houses), len(self.contacts)))

    def send_intro_emails(self, min_duplicate_days,
                          school_filter=[],
                          school_filter_is_include=True,
                          code_filter=[],
                          code_filter_is_include=True):
        self.do_sends(min_duplicate_days, MailType.EMAIL, Contact.send_email, school_filter, school_filter_is_include, code_filter, code_filter_is_include)
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
                          code_filter=[],
                          code_filter_is_include=True):
        self.do_sends(min_duplicate_days, MailType.MAIL, Contact.send_mail, school_filter, school_filter_is_include, code_filter, code_filter_is_include)
        print("Should we log the dates we're contacting people included in the snail mailer? Aka are we sending this batch?")
        if self.prompt_for_bool():
            self.google.confirm_sending_mail()
    def do_sends(self, min_duplicate_days, mail_type, f,
                          school_filter=[],
                          school_filter_is_include=True,
                          code_filter=[],
                          code_filter_is_include=True):
        for contact in self.contacts:
            if self.__filter(contact.data, min_duplicate_days, self.google.get_last_date_for_contact, MailType.MAIL, school_filter, school_filter_is_include, code_filter, code_filter_is_include):
                f(contact, self.google)
        for house in self.houses:
            if self.__filter(house.data, min_duplicate_days, self.google.get_last_date_for_house, MailType.MAIL, school_filter, school_filter_is_include, code_filter, code_filter_is_include):
                f(house, self.google)


    def get_school_list(self):
        return ['UCLA', 'USC', 'Denver', 'Georgia Tech']
    def get_house_code_list(self):
        return ['active', 'suspended']
    def get_contact_code_list(self): 
        return ['agent', 'board', 'general_board', 'undergrad', 'contact']

    def __filter(self, data, min_duplicate_days,
                  min_duplicate_days_func, enum,
                  school_filter=[],
                  school_filter_is_include=True,
                  code_filter=[],
                  code_filter_is_include=True):
        if (data.short_name in school_filter and not school_filter_is_include) \
                or (data.short_name not in school_filter and school_filter_is_include): 
            return False
        if (data.code in code_filter and not code_filter_is_include) \
                or (data.code not in code_filter and code_filter_is_include): 
            print('Skipping Code: {} not included in current selection'.format(data.code))
            return False
        last_date = min_duplicate_days_func(data, enum)
        if datetime.date.today() - last_date < datetime.timedelta(min_duplicate_days):
            print('Skipping when last {} date is {} and today is {} and min_duplicate days is {}'.format(enum, last_date, datetime.date.today(), min_duplicate_days))
            return False
        return True
# one off functions --------------------------------------------------- 
    def update_redirects(self, fn):
        visits = parse_redirect_log(fn)
        print(visits)
        self.google.update_page_visits(visits)



if __name__=='__main__':
    g2 = Google()
    emp = ModelEmployee(g2)
    #emp.update_redirects('/home/tgaldes/Desktop/redirects.csv')

    #emp.send_snail_mail(0, ['USA', 'VCU', 'ODU', 'UNR', 'UW Madison', 'Duke' 'Toledo', 'UCF', 'Nebraska'], True, [], False)
    emp.send_snail_mail(0, ['USC', 'SJSU'], True, ['board'], True)
    #emp.send_snail_mail(0, ['UW'], True, ['active'], True)
    #emp.send_intro_emails(0, ['USC'], True, ['board'], True)


