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

backup_keys = { \
    'chapter_designation' : ['short_name'],
    'name' : ['fraternity']
}



# specific columns
mail_type_enum_to_column_name = {enums.MailType.MAIL : 'mail_dates', enums.MailType.EMAIL : 'email_dates'}
name_column_name = 'name'
code_column_name = 'code'
mail_date_column_name = 'mail_dates'
email_date_column_name = 'email_dates'
address_column_name = 'address'
email_column_name = 'email'
qr_date_column_name = 'qr_date'
links_column_name = 'links'
qr_file_name_column_name = 'qr_code_file_name'
unique_url_visited_column_name = 'unique_url_visited'
unique_url_column_name = 'unique_url'
qr_date_column_name = 'qr_date'
populated_addresses_column_names = 'populated_addresses' 
populated_emails_column_names = 'populated_emails'
populated_total_column_names = 'populated_total'

range_builder = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H', 9: 'I', 10: 'J', 11: 'K', 12: 'L', 13: 'M', 14: 'N', 15: 'O', 16: 'P', 17: 'Q', 18: 'R', 19: 'S', 20: 'T', 21: 'U', 22: 'V', 23: 'W', 24: 'X', 25: 'Y', 26: 'Z'}

# validation
if sheet_names.keys() != column_names.keys():
    raise Exception('sheet names and column names keys do not match')

if sheet_names.keys() != ffill_column_names.keys():
    raise Exception('sheet names and ffill_column_names keys do not match')



# TODO: add the columns for the qr code and website page titles
# for testing, names of columns subject to change
contact_data_header = ['short_name', 'fraternity', name_column_name, address_column_name, 'contact', 'phone', 'linkedin', email_column_name, 'email2', 'email3', 'email4', 'email5', 'email6', links_column_name, code_column_name, 'old', 'notes', 'unlinked_lower_name', 'house_base_short_name', unique_url_column_name, qr_file_name_column_name, qr_date_column_name, 'unique_qr_helper', 'reduced_code', mail_date_column_name, email_date_column_name, unique_url_visited_column_name,
populated_addresses_column_names, populated_emails_column_names, populated_total_column_names, 'house_tuple']

contact_data_header_length = len(contact_data_header)
contact_data_info = [ \
['USC', 'Alpha Tau Omega', 'Curtis Westfall', '11500 Tennessee Ave\nUnit 324\nLos Angeles, CA 90064', '', '', '',  'tgaldes@gmail.com', '', 'board', '0', '', 'curtis-westfall', 'usc-ato', 'https://cleanfloorslockingdoors.com/qr-board-usc-ato-curtis-westfall', 'usc-ato-curtis-westfall-1.png', '20200816', '20200915', '', '','', '', '', '', '', ''], \
['SJSU', 'Theta Chi', 'George Bremer', '629 Gayley Ave\nLos Angeles, CA 90024', '', '', '', 'tgaldes@gmail.com', '', 'undergrad', '0', '', 'george-bremer', 'sjsu-theta-chi', 'https://cleanfloorslockingdoors.com/qr-undergrad-sjsu-theta-chi-george-bremer', 'sjsu-theta-chi-george-bremer-3.png', '20200816', '20200916', '', '', '', '', '','', '', '']]
house_data_header = ['short_name', 'fraternity', address_column_name, 'chapter_designation', 'mailing_address', 'corporate_filing', code_column_name, 'chapter_website', 'alumni_website', 'notes', 'city', 'helper_label', mail_date_column_name, email_date_column_name, 'unlinked_lower_name', 'base_short_name_house_name', unique_url_column_name, qr_file_name_column_name, qr_date_column_name, unique_url_visited_column_name, 'area']
house_data_header_length = len(house_data_header)
house_data_info = [['USC', 'Alpha Tau Omega', '2715 Portland St\nLos Angeles, CA 90007', 'Gamma Xi', 'TODO', 'TODO', 'house', 'chapter_website', 'alumni_website', 'notes', 'city', 'helper_label', '', '', 'alpha-tau-omega', 'usc-ato', 'https://cleanfloorslockingdoors.com/qr-usc-ato', 'usc-ato.png', '20200816', '20200915', 'have_corporate_filing', 'have_alumni_website', 'either', 'have_client_at_this_school', 'number_of_confirmed_emails'], \
['SJSU', 'Theta Chi', '123 S 11th St\nSan Jose, CA 95217', 'Gamma Xi', 'TODO', 'TODO', 'house', 'chapter_website', 'alumni_website', 'notes', 'city', 'helper_label', '', '', 'theta-chi', 'sjsu-theta-chi', 'https://cleanfloorslockingdoors.com/qr-sjsu-theta-chi', 'sjsu-theta-chi.png', '20200816', '20200915', 'have_corporate_filing', 'have_alumni_website', 'either', 'have_client_at_this_school', 'number_of_confirmed_emails']]
