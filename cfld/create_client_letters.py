import os
import pdb
import pandas as pd
from letters import RawLetters

index2blank_lines_est = {0 : 28, 1 : 28, 2 : 28, 3 : 27}


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
# drop rows that we've already mailed
    cast_cols = ['mailed', 'skip']
    for col in cast_cols:
        df[col].fillna(value=0, inplace=True)
    mailed = df[df['mailed'].astype(int) == 1].astype(str)
    df.drop(df[df['mailed'].astype(int) == 1].index, inplace= True)
    print('Dropping {} rows for houses that have already been mailed.'.format(mailed.count()[0]))
    skipped = df[df['skip'].astype(int) == 1].astype(str)
    df.drop(df[df['skip'].astype(int) == 1].index, inplace= True)
    print('Skipping {} chapters that were configured not to run'.format(skipped.count()[0]))
    skipped['name'] = skipped['university'] + ' ' + skipped['fraternity']
    for row in skipped.iterrows():
        print(row[1]['university'] + " " + row[1]['fraternity'])
    df.drop(df.columns[len(csv_header):], axis=1, inplace=True)
    print('Droppting the following rows with incomplete information:')
    for row in df[df.isnull().any(axis=1)].iterrows():
        print(str(row[1]['university']) + " " + str(row[1]['fraternity']))
    df.dropna(inplace=True)
    df = df.astype(str)
    df['chapter_address'] = df['chapter_address'].apply(lambda x : x[:x.find(',')] + ' in' + x.split(',')[1])
    rows = []
    for row in df.itertuples():
        rows.append(list(row)[1:])
    for row in rows:
        for i, item in enumerate(row):
            row[i] = item.replace('Name\t', '').replace('Address\t', '').replace('\n', '\n\t').replace('\t', '').replace('Corporate Owner','').replace('\n', '\n\t').replace('Name', '').replace('Address', '').replace('  ', ' ').replace('  ', ' ').replace('  ', ' ').replace('\t ', '\t')
            if i == 3:
                if row[i][0] == ' ':
                    row[i] = row[i][1:]  # take out the spaces that got condensed to one before name/address
                row[i] = '\t' + row[i] # add tab at the beginning
    #pdb.set_trace()
    return rows

# add or subtract newlines from the end of the string such that there are blank_line_est newlines
def format_string_for_page(s, est):
    count = 0
    for i in s:
        if i == '\n':
            count += 1

    if est < count:
        s = s[:est - count]
    elif count < est:
        s += '\n' * (est - count)
    s+='a'
    return s


def get_targets(n):
    return ['target_' + str(i) for i in range(n)]

def prep_sub_info(row, letter_index_index=-1):
    d = {}
    letter_index = row[letter_index_index]
    del row[letter_index_index]
    targets = get_targets(len(row))
    for i, item in enumerate(row):
        d[targets[i]] = item
    return int(letter_index), d

def process_letter(info):
    letter_index, d = prep_sub_info(info)
    text = RawLetters.raw_letters[letter_index]
    for key in d:
        text = text.replace(key, d[key])
    return format_string_for_page(text, index2blank_lines_est[letter_index])


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







