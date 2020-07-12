class Letter:
    def __init__(self, msg, fields):
        self.msg = msg
        self.fields = fields

letters = \
{
    'board' : Letter('A letter to the board member of the {} Association of {} named {}', (('chapter_designation', 1), ('fraternity', 0), ('name', 0))) \
    ,'undergrad' : Letter('A letter to the undergrad member of {} named {}', (('fraternity', 0), ('name', 0)))
}

backup_keys = { \
    'chapter_designation' : 'short_name'
}
