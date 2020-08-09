class Message:
    def __init__(self, fn, fields):
        self.msg = ''
        with open(fn, 'r') as f:
            for line in f:
                self.msg += line
        self.fields = fields

letters = \
{
    'board' : Message('letters/board.txt', [('name', 0), ('city', 1), ('chapter_designation', 1), ('fraternity', 0), ('name', 0)]),
    'undergrad' : Message('letters/undergrad.txt', [('fraternity', 0), ('name', 0)]),
    'active' : Message('letters/active.txt', [('chapter_designation', 0), ('fraternity', 0), ('short_name', 0), ('address', 0)]),
    'agent' : Message('letters/todo.txt', [('code', 0)]),
    'campaign_chair' : Message('letters/todo.txt', [('code', 0)]),
    'general_board' : Message('letters/todo.txt', [('code', 0)]),
    'general_undergrad' : Message('letters/todo.txt', [('code', 0)]),
    'general_board' : Message('letters/todo.txt', [('code', 0)]),
    'high_value' : Message('letters/todo.txt', [('code', 0)]),
    'suspended' : Message('letters/todo.txt', [('code', 0)])
}

backup_keys = { \
    'chapter_designation' : ['short_name'],
    'name' : ['fraternity']
}

emails = \
{
    'board' : Message('emails/board.txt', [('chapter_designation', 1), ('fraternity', 0), ('name', 0)]),
    'undergrad' : Message('emails/undergrad.txt', [('fraternity', 0), ('name', 0)]),
    'active' : Message('emails/active.txt', [('chapter_designation', 0), ('fraternity', 0), ('short_name', 0), ('address', 0)]),
    'board' : Message('emails/board.txt', [('name', 0), ('chapter_designation', 1), ('fraternity', 0), ('name', 0)]),
    'undergrad' : Message('emails/undergrad.txt', [('fraternity', 0), ('name', 0)]),
    'agent' : Message('emails/todo.txt', [('code', 0)]),
    'campaign_chair' : Message('emails/todo.txt', [('code', 0)]),
    'general_board' : Message('emails/todo.txt', [('code', 0)]),
    'general_undergrad' : Message('emails/todo.txt', [('code', 0)]),
    'general_board' : Message('emails/todo.txt', [('code', 0)]),
    'high_value' : Message('emails/todo.txt', [('code', 0)]),
    'suspended' : Message('emails/todo.txt', [('code', 0)])
}
