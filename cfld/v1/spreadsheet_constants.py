sheet_names = { \
'houses' : 'houses',
'contacts' : 'addresses_clean'}

# can these be dynamically populated?
column_names = { \
'houses' : ['short_name', 'fraternity'], \
'contacts' : ['short_names', 'fraternity']} # TODO: fill the rest of this out

ffill_column_names = { \
'houses' : ['short_name', 'fraternity'], \
'contacts' : ['short_name', 'fraternity']}


# validation
if sheet_names.keys() != column_names.keys():
    raise Exception('sheet names and column names keys do not match')

if sheet_names.keys() != ffill_column_names.keys():
    raise Exception('sheet names and ffill_column_names keys do not match')
