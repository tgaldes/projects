class Message:
    def __init__(self, fn, fields):
        self.msg = ''
        with open(fn, 'r') as f:
            for line in f:
                self.msg += line
        #self.msg = self.msg.format(
        self.fields = fields

# TODO: house -> active / suspended / inactive / etc
letters = \
{
    'board' : Message('letters/board.txt', (('chapter_designation', 1), ('fraternity', 0), ('name', 0))),
    'undergrad' : Message('letters/undergrad.txt', (('fraternity', 0), ('name', 0))),
    'house' : Message('letters/house.txt', (('chapter_designation', 0), ('fraternity', 0), ('short_name', 0), ('address', 0)))
}

backup_keys = { \
    'chapter_designation' : ['short_name'],
    'name' : ['fraternity']
}

emails = \
{
    'board' : Message('emails/board.txt', (('chapter_designation', 1), ('fraternity', 0), ('name', 0))),
    'undergrad' : Message('emails/undergrad.txt', (('fraternity', 0), ('name', 0))),
    'house' : Message('emails/house.txt', (('chapter_designation', 0), ('fraternity', 0), ('short_name', 0), ('address', 0)))
}
