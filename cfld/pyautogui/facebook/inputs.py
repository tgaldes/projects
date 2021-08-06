from collections import namedtuple



# Normal housing groups
group_data = {'USC' :(
             'https://docs.google.com/document/d/1wOmbPiLod6B-WPjF4ygP6JbjqGP8Em4VXPMk0yekX_8',
             '/home/tgaldes/Dropbox/Fraternity PM/Pictures/2715 Portland USC/selections',
             [
                 ('https://www.facebook.com/groups/344453725628321/', 2),
                 ('https://www.facebook.com/groups/housingusc/', 1),
                 ('https://www.facebook.com/groups/apartment.la/', 1)
                 ('https://www.facebook.com/groups/143384839561246/', 3),
             ],
             (1194, 1390), # coords to the 'post' button when we c/p the blurb into the text box
             (1113, 282)  # coords to the area that we check for post pending
        ),
        'UCLA' :
        (
            'asdf',
            'asdf',
            [
                 ('https://www.facebook.com/groups/1835635240040670/', 1)
                 ('https://www.facebook.com/groups/415336998925847/', 1)
                 ('https://www.facebook.com/groups/apartment.la/', 1)
                 ('https://www.facebook.com/groups/143384839561246/', 3),
            ],
             (1194, 1390), # coords to the 'post' button when we c/p the blurb into the text box
             (1113, 282)  # coords to the area that we check for post pending
        ),
        'SJSU' :
        (
            'https://docs.google.com/document/d/1jxyqgdu0EXNK73gg5kcapxTcLc0XilB1qrkAbe31BtU',
            '/home/tgaldes/Dropbox/Fraternity PM/Pictures/SJSU TX/facebook',
            [
                ('https://www.facebook.com/groups/948845475189394/', 1),
                ('https://www.facebook.com/groups/SJSUhousing/', 2), # SJSU
                ('https://www.facebook.com/groups/574981909329531/', 2) # SJSU
            ],
             (1194, 1390), # coords to the 'post' button when we c/p the blurb into the text box
             (1113, 282)  # coords to the area that we check for post pending
        ),
        'Pitt' :
        (
            'asdf',
            'asdf',
            [
                ('https://www.facebook.com/groups/pittoffcampus/', 1),
                ('https://www.facebook.com/groups/1891295347777497/', 1),
                ('https://www.facebook.com/groups/816037598451517/', 1),
                ('https://www.facebook.com/groups/214878512490890/', 1),
                ('https://www.facebook.com/groups/206101910004393/', 1),
                ('https://www.facebook.com/groups/918647024841663/', 1),
                ('https://www.facebook.com/groups/904140896737771/', 1),
            ],
             (1194, 1390), # coords to the 'post' button when we c/p the blurb into the text box
             (1113, 282)  # coords to the area that we check for post pending
        ),
        'UMN' :
        (
            'https://docs.google.com/document/d/17Kx_8SGCm3QA-ArL8o7GU99cOyqjLJX02lJogHlAvKg',
            '/home/tgaldes/Dropbox/Fraternity PM/Pictures/Minnesota Kappa Sigma/Facebook',
            [
                ('https://www.facebook.com/groups/607733796013823/', 1)
                ('https://www.facebook.com/groups/1364804473579405/', 1)
            ],
             (1194, 1390), # coords to the 'post' button when we c/p the blurb into the text box
             (1113, 282)  # coords to the area that we check for post pending
         )
        }
buy_sell_data = {'USC' :(
             'https://docs.google.com/document/d/1wOmbPiLod6B-WPjF4ygP6JbjqGP8Em4VXPMk0yekX_8',
             '/home/tgaldes/Dropbox/Fraternity PM/Pictures/2715 Portland USC/selections',
             [
                 ('https://www.facebook.com/groups/764096300371317/', 3), # USC
                 ('https://www.facebook.com/groups/uschousing/', 2), # USC
                 ('https://www.facebook.com/groups/151027485336692/?ref=gysj', 1), # LA
                 ('https://www.facebook.com/groups/55449183852/', 2), # LA
                 ('https://www.facebook.com/groups/roompiklosangelesroommaterentals', 2), # LA
                 ('https://www.facebook.com/groups/LosAngelesHousingRentals/', 2), # LA
                 ('https://www.facebook.com/groups/1286269061395308/', 2), # LA
                 ('https://www.facebook.com/groups/LA4stay/', 2), # LA
             ],
             'USC Student Housing',
             '500'
        ),
        'SJSU' :
        (
            'https://docs.google.com/document/d/1jxyqgdu0EXNK73gg5kcapxTcLc0XilB1qrkAbe31BtU',
            '/home/tgaldes/Dropbox/Fraternity PM/Pictures/SJSU TX/facebook',
            [
                ('https://www.facebook.com/groups/1153022088056808/', 2),
                ('https://www.facebook.com/groups/1426595240988253/', 3),
                ('https://www.facebook.com/groups/2023562321211089', 3),
                ('https://www.facebook.com/groups/I3027/', 2),
                ('https://www.facebook.com/groups/bayareagradhousing2015', 2),
            ],
             'SJSU Student Housing',
             '650',
        ),
        'UCLA' :
        (
            'asdf',
            'asdf',
            [
                 ('https://www.facebook.com/groups/846176935459516/', 1),
                 ('https://www.facebook.com/groups/437963763011620/', 1),
                 ('https://www.facebook.com/groups/1414484008814397', 1),
                 ('https://www.facebook.com/groups/151027485336692/?ref=gysj', 1), # LA
                 ('https://www.facebook.com/groups/55449183852/', 2), # LA
                 ('https://www.facebook.com/groups/roompiklosangelesroommaterentals', 2), # LA
                 ('https://www.facebook.com/groups/LosAngelesHousingRentals/', 2), # LA
                 ('https://www.facebook.com/groups/1286269061395308/', 2), # LA
                 ('https://www.facebook.com/groups/LA4stay/', 2), # LA
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



