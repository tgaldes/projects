from Contact import Contact


# imported for __main__
from Google import Google
import collections
import spreadsheet_constants
import pickle
import pdb

# TODO: House should inherit from Contact so we can override some function calls and behavior but still take advantage of the IAddressee implemented in Contact
# TODO: House won't have an email address, but not all contacts will be created with a populated email address string, so we'll have to support a Contact instance being an 'IEmailAddressee' even if we don't have an email address
class House(Contact):
    def __init__(self, named_tuple):
        self.data = named_tuple
        self.house_data = named_tuple
        self.datas = [self.data, self.data]

if __name__=='__main__':
    '''g = Google()
    with open('pickles/google.pickle', 'wb') as f:
        pickle.dump(g, f)'''
    with open('pickles/google.pickle', 'rb') as f:
        g2 = pickle.load(f)
    HouseData = collections.namedtuple('HouseData', spreadsheet_constants.house_data_header)
    houses = [HouseData(*x) for x in spreadsheet_constants.house_data_info]
    house_objs = [House(HouseData(*x)) for i, x in enumerate(spreadsheet_constants.house_data_info)]
    for h in house_objs:
        #h.send_email(g) # TODO
        h.send_mail(g2)
        #print(getattr(c.data, 'name'))



