import pyautogui as pag
pag.PAUSE = 1
pag.FAILSAFE = True
from time import sleep
import os

from inputs import all_groups


# hold corrdinates of various clicks we need in a map so that we can run indep of display
group_name_mapping = {1 : 'one_line_group_photo_video', 
                      2 : 'two_line_group_photo_video',
                      3 : 'three_line_group_photo_video'}
                      
all_coords = {
    'l' : # laptop 
        { 'menu' : (100, 100) },
    'm' : # monitor
        { 
            'menu' : (23, 65),
            'chrome' : (168, 170),
            'close_chrome' : (91, 46),
            'url_bar' : (562, 78),
            'one_line_group_photo_video' : (1063, 801),
            'two_line_group_photo_video' : (1063, 831),
            'file_upload_path' : (1202, 250),
            'write_something' : (1144, 590),
            'three_line_group_photo_video' : (1066, 863),
            'tab_one' : (264, 60),
            'tab_two' : (540, 60),
            'google_drive_ready' : (949, 286)
        }
    }
mkey = 'm' # TODO
coords = all_coords[mkey]

# gui constants
# TODO: redshift for non gray pixels
facebook_post_pending_color = (246, 246, 246)
facebook_post_photo_video_color = (122, 183, 103) # green in the button
facebook_post_photo_video_color_bk = (116, 173, 98) # green in the button
#facebook_ready_to_post_color = (69, 117, 225) # white
facebook_ready_to_post_color = (72, 123, 237) # blue
drive_ready_color = (255, 255, 255)
chrome_url_bar = (255, 255, 255)

def mouse_click(item, sleep_secs=0):
    pag.click(*coords[item])
    sleep(sleep_secs)
    pass
def move_to(item):
    pag.moveTo(*coords[item])
def keyboard(s):
    pag.typewrite(s)
def press(*keys):
    pag.hotkey(*keys)
# copy paste the contents of the file to the current clicked element
def copy_paste(s, dest, fn='tmp_input.txt'):
    with open(fn, 'w') as f:
        f.write(s)
        f.flush()
    # copy
    os.system('cat {} | xclip -selection clipboard'.format(fn))
    # select dest
    mouse_click(dest)
    # paste
    press('ctrl', 'v')

def open_tab(url):
    copy_paste(url, 'url_bar')
    sleep(1)
    mouse_click('url_bar')
    press('enter')

def wait_for_screen(pixel, match, item, x=0, y=0):
    if x == 0 and y == 0:
        x, y = coords[item]
    count = 0
    while True:
        if wait_loop(pixel, match, x, y, count):
            return
        sleep(1)
        count += 1

def wait_for_screen_and_scroll(pixels, match, item, x=0, y=0):
    if x == 0 and y == 0:
        x, y = coords[item]
    count = 0
    while True:
        pag.scroll(1000)
        for pixel in pixels:
            if wait_loop(pixel, match, x, y, count):
                return
        sleep(1)
        count += 1

def wait_loop(pixel, match, x, y, count):
    if match == pag.pixelMatchesColor(x, y, pixel):
        return True
    screen = pag.screenshot()
    print('pixel {} coords {} matching {} actual {}'.format((x, y), pixel, match, screen.getpixel((x, y))))
    if count > 120:
        print('timing out after two minutes, still loc {} pixel to match {} matching {}'.format((x, y), pixel, match))
        exit(1)
    return False

#def run_group(google_doc_link, folder_path, group_tup, post_coords):
def run_group(nt): #google_doc_link, folder_path, group_tup, post_coords):
    mouse_click('menu')
    keyboard('Chrome')
    mouse_click('chrome')
    wait_for_screen(chrome_url_bar, True, 'url_bar')
    open_tab(nt.group_link)
    press('ctrl', 't')
    open_tab(nt.google_drive_link)
    press('ctrl', 'pageup') # back to facebook tab
    move_to(group_name_mapping[nt.group_name_length]) # move cursor back to main page
    wait_for_screen_and_scroll([facebook_post_photo_video_color, facebook_post_photo_video_color_bk, (121, 177, 105)], True, group_name_mapping[nt.group_name_length])
    mouse_click(group_name_mapping[nt.group_name_length]) # click the 'photo/video button'
    copy_paste(nt.folder_path, 'file_upload_path')
    sleep(1)
    press('backspace')
    press('enter')
    sleep(1)
    # select all photos and go
    press('ctrl', 'a')
    press('enter')
    sleep(2) # takes some time to upload the photos

    #press('ctrl', 'pagedown') # to google doc
    mouse_click('tab_two')
    wait_for_screen(drive_ready_color, True, 'google_drive_ready')
    mouse_click('google_drive_ready')
    press('ctrl', 'a') # select the text
    sleep(1)
    press('ctrl', 'c') # copy the text
    sleep(1)
    #press('ctrl', 'pageup') # back to facebook
    mouse_click('tab_one')
    sleep(1)
    mouse_click('write_something')
    press('ctrl', 'v')
    wait_for_screen(facebook_ready_to_post_color, True, '', *nt.post_button_coords)
    pag.click(*(nt.post_button_coords))
    sleep(5) # we still need to be able to wait for the post pending screen

    wait_for_screen(facebook_post_pending_color, False, '', *nt.post_pending_coords)
    sleep(1)
    mouse_click('close_chrome')

if __name__=='__main__':
    for data in all_groups:
        run_group(data)


