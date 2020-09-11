from collections import namedtuple



# Normal housing groups
group_data = {'USC' :(
             'https://docs.google.com/document/d/1wOmbPiLod6B-WPjF4ygP6JbjqGP8Em4VXPMk0yekX_8',
             '/home/tgaldes/Dropbox/Fraternity PM/Pictures/2715 Portland USC/selections',
             [
                 ('https://www.facebook.com/groups/1621705121404017/', 2),
                 ('https://www.facebook.com/groups/695435553986189/', 2), 
                 ('https://www.facebook.com/groups/344453725628321/', 2),
                 ('https://www.facebook.com/groups/344314769393545', 2),
                 ('https://www.facebook.com/groups/212185346023652/', 1),
                 ('https://www.facebook.com/groups/143384839561246/', 3),
                 ('https://www.facebook.com/groups/161010671290969/', 1)
             ],
             (1194, 1419), # coords to the 'post' button when we c/p the blurb into the text box
             (1113, 282)  # coords to the area that we check for post pending
        ),
        'SJSU' :
        (
            'https://docs.google.com/document/d/1jxyqgdu0EXNK73gg5kcapxTcLc0XilB1qrkAbe31BtU',
            '/home/tgaldes/Dropbox/Fraternity PM/Pictures/SJSU TX/facebook',
            [
                ('https://www.facebook.com/groups/948845475189394/', 1),
                ('https://www.facebook.com/groups/SJSUhousing/', 2),
                ('https://www.facebook.com/groups/574981909329531/', 2)
            ],
             (1194, 1419), # coords to the 'post' button when we c/p the blurb into the text box
             (1113, 282)  # coords to the area that we check for post pending
        ),
        'UMN' :
        (
            'https://docs.google.com/document/d/17Kx_8SGCm3QA-ArL8o7GU99cOyqjLJX02lJogHlAvKg',
            '/home/tgaldes/Dropbox/Fraternity PM/Pictures/Minnesota Kappa Sigma/Facebook',
            [
                ('https://www.facebook.com/groups/439773589790851/', 3),
                ('https://www.facebook.com/groups/153997765269550/', 2),
                ('https://www.facebook.com/groups/607733796013823/', 1)
            ],
             (1194, 1419), # coords to the 'post' button when we c/p the blurb into the text box
             (1113, 282)  # coords to the area that we check for post pending
         )
        }
buy_sell_data = {'USC' :(
             'https://docs.google.com/document/d/1wOmbPiLod6B-WPjF4ygP6JbjqGP8Em4VXPMk0yekX_8',
             '/home/tgaldes/Dropbox/Fraternity PM/Pictures/2715 Portland USC/selections',
             [
                 #('https://www.facebook.com/groups/151027485336692/?ref=gysj', 1),
                 #('https://www.facebook.com/groups/55449183852/', 2), 
                 #('https://www.facebook.com/groups/roompiklosangelesroommaterentals', 2),
                 ('https://www.facebook.com/groups/LosAngelesHousingRentals/', 2),
                 ('https://www.facebook.com/groups/1286269061395308/', 2),
                 ('https://www.facebook.com/groups/LA4stay/', 2),
             ],
             'USC Student Housing',
             '550'
        ),
        'SJSU' :
        (
            'https://docs.google.com/document/d/1jxyqgdu0EXNK73gg5kcapxTcLc0XilB1qrkAbe31BtU',
            '/home/tgaldes/Dropbox/Fraternity PM/Pictures/SJSU TX/facebook',
            [
                #('https://www.facebook.com/groups/1153022088056808/', 2),
                #('https://www.facebook.com/groups/1426595240988253/', 3),
                #('https://www.facebook.com/groups/2023562321211089', 3),
                #('https://www.facebook.com/groups/I3027/', 2),
                ('https://www.facebook.com/groups/bayareagradhousing2015', 2),
            ],
             'SJSU Student Housing',
             '650',
        ),
        'UMN' :
        (
            'https://docs.google.com/document/d/17Kx_8SGCm3QA-ArL8o7GU99cOyqjLJX02lJogHlAvKg',
            '/home/tgaldes/Dropbox/Fraternity PM/Pictures/Minnesota Kappa Sigma/Facebook',
            [
                ('https://www.facebook.com/groups/Minneapolisrentals/', 3),
                ('https://www.facebook.com/groups/TwinCityRentals/', 3),
            ],
            'UMN Student Housing',
            '750',
         ),
        }

GroupData = namedtuple('GroupData', ['google_drive_link', 'folder_path', 'group_link', 'group_name_length', 'post_button_coords', 'post_pending_coords', 'short_name'])
BuySellData = namedtuple('BuySellData', ['google_drive_link', 'folder_path', 'group_link', 'group_name_length', 'short_name', 'title', 'price'])

all_groups = []
for short_name in group_data:
    for group in group_data[short_name][2]:
        school = group_data[short_name]
        data = GroupData(school[0], school[1], group[0], group[1], school[3], school[4], short_name)
        all_groups.append(data)

all_buy_sells = []
for short_name in buy_sell_data:
    for group in buy_sell_data[short_name][2]:
        school = buy_sell_data[short_name]
        data = BuySellData(school[0], school[1], group[0], group[1], short_name, school[3], school[4])
        all_buy_sells.append(data)



