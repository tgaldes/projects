import os



# list of tuples in form
#[(link to google blurb doc, path to pictures folder, [fb group link, fb group link...]), ...]
info = [(
        # USC
         'https://docs.google.com/document/d/1wOmbPiLod6B-WPjF4ygP6JbjqGP8Em4VXPMk0yekX_8/edit',
         '/home/tgaldes/Dropbox/Fraternity PM/Pictures/2715 Portland USC/selections',
         [#'https://www.facebook.com/groups/344314769393545', 
         #'https://www.facebook.com/groups/344453725628321/',
         #'https://www.facebook.com/groups/212185346023652/',
         #'https://www.facebook.com/groups/143384839561246/',  TODO: this group name is 3 lines long so we miss the 'post photo' button
         'https://www.facebook.com/groups/695435553986189/', 
         'https://www.facebook.com/groups/161010671290969/',
         'https://www.facebook.com/groups/1621705121404017/?ref=br_rs'])]

fn = 'cnee_console_information.txt'
sep = '\n\n\n\n'
cnee_cmd = 'cnee --replay -f post_group.xnl -ns'



def run_group(google_doc_link, folder_path, group_link):
# prep the file
    with open(fn, 'w') as f:
        f.write(google_doc_link)
        f.write(sep)
        f.write(folder_path)
        f.write(sep)
        f.write(group_link)
        f.write(sep)

    os.system(cnee_cmd)
    exit(1)


if __name__=='__main__':
    for school in info:
        for group in school[2]:
            run_group(school[0], school[1], group)
