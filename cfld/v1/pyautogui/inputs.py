from collections import namedtuple
school_data = [(
        # USC
         'https://docs.google.com/document/d/1wOmbPiLod6B-WPjF4ygP6JbjqGP8Em4VXPMk0yekX_8/edit',
         '/home/tgaldes/Dropbox/Fraternity PM/Pictures/2715 Portland USC/selections',
         [
         ('https://www.facebook.com/groups/1621705121404017/', 2),
         ('https://www.facebook.com/groups/695435553986189/', 2), 
         ('https://www.facebook.com/groups/344453725628321/', 2),
         ('https://www.facebook.com/groups/344314769393545', 2),
         ('https://www.facebook.com/groups/212185346023652/', 1),
         ('https://www.facebook.com/groups/143384839561246/', 3),
         ('https://www.facebook.com/groups/161010671290969/', 1)],
         (1194, 1419), # coords to the 'post' button when we c/p the blurb into the text box
         (1113, 282)  # coords to the area that we check for post pending
        )]

GroupData = namedtuple('GroupData', ['google_drive_link', 'folder_path', 'group_link', 'group_name_length', 'post_button_coords', 'post_pending_coords'])

all_groups = []
for school in school_data:
    for group in school[2]:
        data = GroupData(school[0], school[1], group[0], group[1], school[3], school[4])
        all_groups.append(data)
        

