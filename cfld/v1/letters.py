class Message:
    def __init__(self, msg, fields):
        self.msg = msg
        self.fields = fields

letters = \
{
    'board' : Message('A letter to the board member of the {} Association of {} named {}', (('chapter_designation', 1), ('fraternity', 0), ('name', 0))) \
    ,'undergrad' : Message('A letter to the undergrad member of {} named {}', (('fraternity', 0), ('name', 0)))
}

backup_keys = { \
    'chapter_designation' : 'short_name'
}

emails = \
{
    'board' : Message('An email to the board member of the {} Association of {} named {}', (('chapter_designation', 1), ('fraternity', 0), ('name', 0))) \
    ,'undergrad' : Message('An email to the undergrad member of {} named {}', (('fraternity', 0), ('name', 0)))
}
