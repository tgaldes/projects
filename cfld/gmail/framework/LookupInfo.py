import pdb

from framework.Logger import Logger


class LookupInfo(Logger):
    def __init__(self, data):
        super(LookupInfo, self).__init__(__class__)
        self.info = {}
        for row in data:
            if row[0]:
                last_key = row[0]
                if row[0] in self.info:
                    raise Exception('Duplicate key in lookup info. \'{}\' specified twice.'.format(row[0]))
                else:
                    self.info[row[0]] = {}
            # add value to dictionary
            if len(row) > 2:
                self.info[last_key][row[1]] = row[2]
            else:
                self.info[last_key][row[1]] = ''
        print(self.info)

    def lookup_info(self, key_a, key_b):
        return self.info[key_a][key_b]

li = LookupInfo
