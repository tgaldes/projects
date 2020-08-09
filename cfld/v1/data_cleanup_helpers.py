
def ffill(ll, col_names):
    if (len(ll)) < 3:
        return

    last_vals = {}
    indices = {}
    for name in col_names:
# map column name to index
        indices[name] = ll[0].index(name)
# map index to last value
        last_vals[indices[name]] = ll[1][indices[name]]

    for i in range(2, len(ll)): # row
        for j in indices.values(): # column
# if we are a '', forward fill
            if ll[i][j] == '':
                ll[i][j] = last_vals[j]
# otherwise update the value we'll forward fill
            else:
                last_vals[j] = ll[i][j]
    return ll

def remove_empty_rows(ll):
    # trim the rows off the end
    ll_ = []
    for i in ll:
        if i and i[0]: ll_.append(i)
    ll = ll_
    return ll

def pad_short_rows(ll):
    mx = 0
    for i in ll:
        if len(i) > mx:
            mx = len(i)
    for i in ll:
        i.extend(['' for x in range(mx - len(i))])
    return ll

def clean(ll, columns):
    return ffill(pad_short_rows(remove_empty_rows(ll)), columns)







