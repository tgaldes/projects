class Message:
    def __init__(self, msg, fields):
        self.msg = msg
        self.fields = fields

letters = \
{
    'board' : Message('\tA letter to the board member of the {} Association of {} named {}. Now imagine this is the end of the paragraph.\n\n\tNow imagine this is the start of another paragraph. Now this paragraph, like all paragraphs, must come to an end. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea \
    commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\n\n\tFear not! The ending of one paragraph is the start of another (usually). It is with eyes to the future that the letter concludes. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna \
    aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\n\n\n\n\nBest,\nTyler Galdes\nClean Floors & Locking Doors\n', (('chapter_designation', 1), ('fraternity', 0), ('name', 0))) \
    ,'undergrad' : Message('A letter to the undergrad member of {} named {}', (('fraternity', 0), ('name', 0)))
}

backup_keys = { \
    'chapter_designation' : 'short_name'
}

emails = \
{
    'board' : Message('An email to the board member of the {} Association of {} named {}. Now imagine this is the end of the paragraph.\n\n\tNow imagine this is the start of another paragraph. Now this paragraph, like all paragraphs, must come to an end.\n\n\tFear not! The ending of one paragraph is the start of another (usually). It is with eyes to the future that the letter concludes.\n\nBest,\nTyler Galdes\nClean Floors & Locking Doors\n', (('chapter_designation', 1), ('fraternity', 0), ('name', 0))) \
    ,'undergrad' : Message('An email to the undergrad member of {} named {}', (('fraternity', 0), ('name', 0)))
}
