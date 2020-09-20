import pdb
from copy import copy
from spreadsheet_constants import bullet_code, end_bullet_code, qr_date_column_name, qr_file_name_column_name, backup_keys
import datetime

def safe_get_attr(tup, key, alt_tups=[]):
    try:
        attr = getattr(tup, key)
        if attr != '':
            return attr
    except:
        pass
        
    alt_tups_ = copy(alt_tups)
    alt_tups_.insert(0, tup)
    for backup_key in backup_keys[key]:
        for current_tup in alt_tups_:
            try:
                attr = getattr(current_tup, backup_key)
                if attr != '':
                    return attr
            except:
                pass # keep looking at backup keys
    # When we get here we didn't find any of the backup keys
    raise Exception('Looking through data tuples for key: {} -> backup_keys: {} yielded the empty string. Data tuples: {}'.format(key, backup_keys[key], alt_tups_))


# Return list of tuples [('text in here', bool isBullet)...]
def parse_for_bullets(msg):
    tups = []
    parsing_bullet = False
    i = 0
    current_start_index = 0
    while i < len(msg):
# end check
        if parsing_bullet and i + len(end_bullet_code) >= len(msg):
            if msg[i:] != end_bullet_code:
                raise Exception('Unclosed bullet in: {}'.format(msg))
            tups.append((msg[current_start_index:i], True))
            return tups
        elif not parsing_bullet and i + len(bullet_code) >= len(msg):
            tups.append((msg[current_start_index:], False))
            return tups
        # finish a bullet, start a non bullet
        elif parsing_bullet and msg[i:i+len(end_bullet_code)] == end_bullet_code:
            tups.append((msg[current_start_index:i], True))
            i += len(end_bullet_code)
            current_start_index = i
            parsing_bullet = False
            continue
        # finish a non bullet, start a bullet
        elif not parsing_bullet and msg[i:i+len(bullet_code)] == bullet_code:
            tups.append((msg[current_start_index:i], False))
            i += len(bullet_code)
            current_start_index = i
            parsing_bullet = True
            continue
        i += 1
        # continue parse

def get_qr_code_url(data):
   base = 'https://cleanfloorslockingdoors.com/wp-content/uploads/' 
   qr_date = getattr(data, qr_date_column_name)
   fn = getattr(data, qr_file_name_column_name)
   qr_year = qr_date[:4]
   qr_month = qr_date[4:6]
   return base + qr_year + '/' + qr_month + '/' + fn

def parse_redirect_log(fn):
    csv = []
    started = False;
    visits = []
    with open(fn, 'r') as f:
        for line in f:
            if 'Select All' in line and 'Source URL' in line:
                started = True
                continue
            if not started:
                continue
            if 'RSS' in line:
                break
            csv.append(line)
    parsing_date = True
    for line in csv:
        cells = line.split(',')
        if parsing_date:
            print(cells)
            ds = cells[1][1:]# will get 'September 15'
            year = cells[2].split()[0] # will get '2020'
            date = datetime.datetime.strptime(ds + ' ' + year, '%B %d %Y').date()
            parsing_date = False
        else:
            url = cells[1].split('A')[0]
            visits.append((url, date))
            parsing_date = True
    return visits


if __name__=='__main__':
    print(parse_for_bullets('paragraph one\nBULLEThere are some bullets\nhere\'s another\nlast one\nENDBULLETText continues in the next paragraph\nlast paragraphBULLEThere are some bullets\nhere\'s another\nlast one\nENDBULLET'))
