import os
import pdb
import pandas as pd
letter = "\n\n\ntarget_3\n\n\n\n\n\n\n\n\nTo whom it may concern,\n\nClean Floors and Locking Doors Inc- Get the most out of your chapter house.\n\nThe chapter house is the foundation of solvency for most fraternities- bringing in income and giving the fraternity the security to invest in the future. target_0 target_2 Clean Floors and Locking Doors Inc. believes that fraternities can invest in their future by increasing the revenue the chapter house brings in over summer. To that end, we provide end to end management of summer fraternity operations, connecting college aged persons looking for seasonal housing to seasonal openings in fraternities. Further, we take the burden of management off the alumni board and undergraduates- we advertise, professionally handle the back and forth with potential tenants, sign leases, collect rent, and take care of any and every tenant issue that comes up over the summer. For those in search of the answer to their summer revenue dip, look no further than Clean Floors and Locking Doors Inc.\n\nAt Clean Floors and Locking Doors we believe in delivering a great living experience to our  Floors & Locking Doors\n\nBest,\nTyler Galdes\nClean Floors & LockingDoors\n\n"

blank_line_est = 35


rows = [['USC', 'ATO', 'Alpha Tau Omega', 'Zeta Beta Of Alpha Tau Omega And Building Corporation\nC/O Gregory Castle\n10960 Wilshire Blvd #1510\nLos Angeles, CA 90024'], \
        ['SJSU', 'TX', 'Theta Chi', 'Fraternity Housing Corporation\nC/O Larry S Wiese\nPO Box 1865\nLexington, VA 24450']]
rows *= 5

csv_header = ['University', 'Letters', 'Chapter', 'mailing address']

# read the csv, drop columns we don't need, and return of list of rows in the format
# [[uni, letters/nickname, chapter name, mail dest], [....
def get_chapter_info(fn):
    df = pd.read_csv(fn)
    df.drop(df.columns[len(csv_header):], axis=1, inplace=True)
    df.dropna(inplace=True)
    df = df.astype(str)
    rows = []
    for row in df.itertuples():
        rows.append(list(row)[1:])
    for row in rows:
        for i, item in enumerate(row):
            row[i] = item.replace('Name\t', '').replace('Address\t', '')
    pdb.set_trace()
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

def populate_dicts(row):
    d = {}
    targets = get_targets(len(row))
    for i, item in enumerate(row):
        d[targets[i]] = item
    return d

def process_letter(info, raw_text):
    d = populate_dicts(info)
    ret = raw_text
    for key in d:
        ret = ret.replace(key, d[key])
    return format_string_for_page(ret)


if __name__=='__main__':
    letters = ''
    rows = get_chapter_info('a.csv')
    for fraternity_info in rows:
        letters += process_letter(fraternity_info, letter)
    out_fn = 'test.txt'
    with open(out_fn, 'w') as f:
        f.write(letters)

    print('copying {} to the clipboard'.format(out_fn))
    os.system('xclip -sel clip test.txt')







