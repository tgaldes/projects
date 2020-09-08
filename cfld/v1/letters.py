import pdb
from global_funcs import safe_get_attr
class Message:
    def __init__(self, fn, fields):
        self.msg = ''
        with open(fn, 'r') as f:
            for line in f:
                self.msg += line
        self.fields = fields

    def format_letter(self, datas):
        attrs = []
        for tup in self.fields:
            if len(tup) == 1:
                attrs.append(tup[0])
            elif len(tup) == 2:
                attrs.append(safe_get_attr(datas[tup[1]], tup[0], datas).title())
            elif len(tup) == 6: # a corporation name
                try:
                    attr = ''
                    attr = getattr(datas[tup[1]], tup[0])
                except AttributeError as e: # Mising the attribute
                    print(str(e) + ' using default value')
                if attr == '':
                    attrs.append(tup[-1]) # default value
                else:
                    attrs.append(tup[2] + attr + tup[3])
            elif len(tup) == 5: # a name
                try:
                    attr = ''
                    attr = getattr(datas[tup[1]], tup[0])
                except AttributeError as e: # Mising the attribute
                    print(str(e) + ' using default value')
                if attr == '':
                    attrs.append(tup[-1]) # default value
                else:
                    attrs.append(tup[2] + attr.split()[-1].capitalize() + tup[3])
            else:
                print(tup)
                raise Exception('Unsupported tuple len (not 1, 2, 4, or 5): '.format(tup))
        return self.msg.format(*attrs)
letters = \
{
    'board' : Message('letters/board.txt', [('name', 0, 'Dear Mr. ', ',', 'To whom it may concern,'), ('chapter_designation', 1), ('fraternity', 0)]),
    'undergrad' : Message('letters/undergrad.txt', [('name', 0, 'Dear Mr. ', ',', 'To whom it may concern,'), ('chapter_designation', 1), ('fraternity', 0)]),
    'active' : Message('letters/undergrad.txt', [('name', 0, 'Dear Mr. ', ',', 'To whom it may concern,'), ('chapter_designation', 1), ('fraternity', 0)]),
    'agent_corp' : Message('letters/agent.txt', [('name', 0, 'To ', ',', 'To whom it may concern,', 'unused'), ('chapter_designation', 1), ('fraternity', 0)]),
    'agent' : Message('letters/agent.txt', [('name', 0, 'Dear Mr. ', ',', 'To whom it may concern,'), ('chapter_designation', 1), ('fraternity', 0)]),
    'agent_female' : Message('letters/agent.txt', [('name', 0, 'Dear Mrs. ', ',', 'To whom it may concern,'), ('chapter_designation', 1), ('fraternity', 0)]),
    'campaign_chair' : Message('letters/board.txt', [('name', 0, 'Dear Mr. ', ',', 'To whom it may concern,'), ('chapter_designation', 1), ('fraternity', 0)]),
    'general_board' : Message('letters/board.txt', [('name', 0, 'Dear Mr. ', ',', 'To whom it may concern,'), ('chapter_designation', 1), ('fraternity', 0)]),
    'general_undergrad' : Message('letters/undergrad.txt', [('name', 0, 'Dear Mr. ', ',', 'To whom it may concern,'), ('chapter_designation', 1), ('fraternity', 0)]),
    'high_value' : Message('letters/board.txt', [('name', 0, 'Dear Mr. ', ',', 'To whom it may concern,'), ('chapter_designation', 1), ('fraternity', 0)]),
    'suspended' : Message('letters/board.txt', [('name', 0, 'Dear Mr. ', ',', 'To whom it may concern,'), ('chapter_designation', 1), ('fraternity', 0)])
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
    'undergrad' : Message('emails/undergrad.txt', [('fraternity', 0), ('name', 0)]),
    'agent' : Message('emails/todo.txt', [('code', 0)]),
    'campaign_chair' : Message('emails/todo.txt', [('code', 0)]),
    'general_board' : Message('emails/todo.txt', [('code', 0)]),
    'general_undergrad' : Message('emails/todo.txt', [('code', 0)]),
    'general_board' : Message('emails/todo.txt', [('code', 0)]),
    'high_value' : Message('emails/todo.txt', [('code', 0)]),
    'suspended' : Message('emails/todo.txt', [('code', 0)])
}

# TODO: how to put names on the letters?
# board/undergrad/agent: name
# general board: the alpha zeta association of theta xi OR the alpha zeta of theta xi house corporation
# general undergrad: alpha zeta of theta xi
# active/suspended: alpha zeta of theta xi house corporation and populate it with a board letter, there's no chapter there so hope someone is actually reading the mail
