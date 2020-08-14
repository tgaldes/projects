import enums
sheet_names = { \
'houses' : 'houses',
'contacts' : 'addresses_clean'}

columns_that_define_unique_house = 2 # school, fraternity
columns_that_define_unique_contact = columns_that_define_unique_house + 1 # school, fraternity, name
# can these be dynamically populated?
column_names = { \
'houses' : ['short_name', 'fraternity'], \
'contacts' : ['short_name', 'fraternity']} # TODO: fill the rest of this out

ffill_column_names = { \
'houses' : ['short_name', 'fraternity'], \
'contacts' : ['short_name', 'fraternity']}

bullet_code = 'BULLET'
end_bullet_code = 'END' + bullet_code


# specific columns
mail_type_enum_to_column_name = {enums.MailType.MAIL : 'mail_dates', enums.MailType.EMAIL : 'email_dates'}
mail_date_column_name = 'mail_dates'
email_date_column_name = 'email_dates'
address_column_name = 'address'

range_builder = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H', 9: 'I', 10: 'J', 11: 'K', 12: 'L', 13: 'M', 14: 'N', 15: 'O', 16: 'P', 17: 'Q', 18: 'R', 19: 'S', 20: 'T', 21: 'U', 22: 'V', 23: 'W', 24: 'X', 25: 'Y', 26: 'Z'}

# validation
if sheet_names.keys() != column_names.keys():
    raise Exception('sheet names and column names keys do not match')

if sheet_names.keys() != ffill_column_names.keys():
    raise Exception('sheet names and ffill_column_names keys do not match')



# TODO: add the columns for the qr code and website page titles
# for testing, names of columns subject to change
contact_data_header = ['short_name', 'fraternity', 'name', 'address', 'contact', 'phone', 'linkedin', 'email', 'links', 'code', 'old', 'notes', 'mail_dates', 'helper_label', 'is_confirmed_email', 'is_confirmed_board_address', 'have_confirmed_email_for_alumni', 'have_board_address_for_house', 'have_client_at_school', 'house_tuple']
contact_data_header_length = len(contact_data_header)
contact_data_info = [ \
['USC', 'Alpha Tau Omega', 'Curtis Westfall', '11500 Tennessee Ave\nUnit 324\nLos Angeles, CA 90064', '', '', '',  'tgaldes@gmail.com', '', 'board', '0', '', '', '','', '', '', '', ''], \
['SJSU', 'Theta Chi', 'George Bremer', '629 Gayley Ave\nLos Angeles, CA 90024', '', '', '', 'tgaldes@gmail.com', '', 'undergrad', '0', '', '', '', '', '', '','', '']]
house_data_header = ['short_name', 'fraternity', 'address', 'chapter_designation', 'mailing_address', 'corporate_filing', 'code', 'chapter_website', 'alumni_website', 'notes', 'city', 'mail_dates', 'email_dates', 'have_corporate_filing', 'have_alumni_website', 'either', 'have_client_at_this_school', 'helper_label', 'number_of_confirmed_emails']
house_data_header_length = len(house_data_header)
house_data_info = [['USC', 'Alpha Tau Omega', '2715 Portland St\nLos Angeles, CA 90007', 'Gamma Xi', 'TODO', 'TODO', 'house', 'TODO', 'TODO', 'TODO', 'TODO', 'TODO', 'TODO', 'TODO', 'TODO', 'TODO', 'TODO', 'helper_label', 'TODO'], \
['SJSU', 'Theta Chi', '123 S 11th St\nSan Jose, CA 95217', 'Gamma Xi', 'TODO', 'TODO', 'house', 'TODO', 'TODO', 'TODO', 'TODO', 'TODO', 'TODO', 'TODO', 'TODO', 'TODO', 'TODO', 'helper_label', 'TODO']]

