import os
import pdb
import pandas as pd
letters = ["""Clean Floors & Locking Doors\n11500 Tennessee Ave #324\nLos Angeles CA, 90064\n\n\n\n\ttarget_4\n\n\n\n\nTo whom it may concern,\n\nI'm reaching out on behalf of Clean Floors & Locking Doors Inc to discuss helping target_1 at target_0 drastically increase the revenue it brings in over summer.\n\nClean Floors & Locking Doors believes that fraternities can invest in their future by increasing the revenue the chapter house brings in over summer. To that end, we connect college aged
persons looking for seasonal housing to seasonal openings in fraternities. Further, we take the burden of management off the alumni board and undergraduates- advertising, professionally handling the back and forth with potential tenants, signing leases, collecting rent, and taking care of any and every tenant issue that comes up over the summer (you can check out an example of our work at 649gayley.com). We are looking to expand beyond UCLA to other campuses in high demand areas, such as
target_2, for summer of 2020.\n\nOur ideal client has a small chapter, full sized chapter house, and struggles to fill their chapter house during the summer- resorting to renting their rooms at below the market rate or leaving rooms empty for the duration of the break. For example, a prospective client at SJSU has a 50 person fraternity house that has brought in roughly $10,000 per month over summer in recent years. We are optimistic that we will be able to double that income, AFTER management
costs, meaning an extra $30,000 in the association's bank account at the end of summer.\n\nIf the target_3 chapter of target_1 fits this profile, I would love to discuss your summer operations and see if working with Clean Floors & Locking Doors would benefit you. Please reach out to tyler@cleanfloorslockingdoors.com and we can figure out a time for a phone call.\n\nBest,\nTyler Galdes\nClean Floors & Locking Doors\n\n\n""" \
, \

""" two """ \
""" three """]


blank_line_est = 28


rows = [['USC', 'Alpha Tau Omega', 'downtown Los Angeles', 'Gamma Xi', 'Zeta Beta Of Alpha Tau Omega And Building Corporation\n\tC/O Gregory Castle\n\t10960 Wilshire Blvd #1510\n\tLos Angeles, CA 90024'], \
        ['SJSU', 'Theta Chi', 'downtown San Jose', 'Alpha Zeta', 'Fraternity Housing Corporation\n\tC/O Larry S Wiese\n\tPO Box 1865\n\tLexington, VA 24450']]
rows *= 5

csv_header = ['university', 'fraternity', 'location', 'mailing_address', 'chapter_address', 'letter_index']
def find_2nd(string, substring):
   print(string[string.find(substring) + 1:].find(substring) + string.find(substring) + 1)
   return string[string.find(substring) + 1:].find(substring) + string.find(substring) + 1

# read the csv, drop columns we don't need, and return of list of rows in the format
# [[uni, letters/nickname, chapter name, mail dest], [....
def get_chapter_info(fn):
    df = pd.read_csv(fn)
# TODO: drop skip rows and print
    skipped = df[df['skip'].astype(int) == 1].astype(str)
    print('Skipping {} chapters that were configured not to run'.format(skipped.count()[0]))
    skipped['name'] = skipped['university'] + ' ' + skipped['fraternity']
    print(skipped.head(skipped.count()[0]))
    df.drop(df.columns[len(csv_header):], axis=1, inplace=True)
    df.dropna(inplace=True) # TODO: print out chapters/unis we dropped
    df = df.astype(str)
    pdb.set_trace()
    df['chapter_address'] = df['chapter_address'].apply(lambda x : x[:x.find(',')] + ' in' + x.split(',')[1])
    pdb.set_trace()
    rows = []
    for row in df.itertuples():
        rows.append(list(row)[1:])
    for row in rows:
        for i, item in enumerate(row):
            row[i] = item.replace('Name\t', '').replace('Address\t', '').replace('\n', '\n\t')
    return rows

# add or subtract newlines from the end of the string such that there are blank_line_est newlines
def format_string_for_page(s):
    count = 0
    for i in s:
        if i == '\n':
            count += 1

    if blank_line_est < count:
        print('removing the last {} chars from the string.'.format(-1 *(blank_line_est - count)))
        s = s[:blank_line_est - count]
    elif count < blank_line_est:
        print('adding {} chars to the string.'.format(blank_line_est - count))
        s += '\n' * (blank_line_est - count)
    return s


def get_targets(n):
    return ['target_' + str(i) for i in range(n)]

def prep_sub_info(row, letter_index_index=-1):
    d = {}
    letter_index = row[letter_index_index]
    row = row[:letter_index_index] + row[letter_index_index + 1:] # take out the letter index fromt the dict
    targets = get_targets(len(row))
    for i, item in enumerate(row):
        d[targets[i]] = item
    return letter_index, d

def process_letter(info):
    letter_index, d = prep_sub_info(info)
    raw_text = letters[letter_index]
    for key in d:
        ret = ret.replace(key, d[key])
    return format_string_for_page(ret)


if __name__=='__main__':
    letters = ''
    rows = get_chapter_info('a.csv')
    for fraternity_info in rows:
        letters += process_letter(fraternity_info)
    out_fn = 'test.txt'
    with open(out_fn, 'w') as f:
        f.write(letters)

    print('copying {} to the clipboard'.format(out_fn))
    os.system('xclip -sel clip test.txt')







