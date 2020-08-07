import letters
import pdb

def safe_get_attr(tup, key, alt_tups=[]):
    try:
        attr = getattr(tup, key)
        if attr != '':
            return attr
    except:
        pass
        
    alt_tups.insert(0, tup)
    for backup_key in letters.backup_keys[key]:
        for current_tup in alt_tups:
            try:
                attr = getattr(current_tup, backup_key)
                if attr != '':
                    return attr
            except:
                pass # keep looking at backup keys
    # When we get here we didn't find any of the backup keys
    raise Exception('Looking through data tuples for key: {} -> backup_keys: {} yielded the empty string. Data tuples: {}'.format(key, letters.backup_keys[key], alt_tups))

