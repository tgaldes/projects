import pdb
import pyautogui as pag
pag.PAUSE = 1
pag.FAILSAFE = True
from time import sleep
import os

from facebook.inputs import all_groups, all_buy_sells
from facebook.constants import * # TODO refactor three
from utils import * # TODO: refactor three



def open_buy_sell_window(nt):
    count = 0
    while True:
        move_to(buy_sell_name_mapping[nt.group_name_length])
        # we need to move the mouse off the button in case the page loads with the cursor already on the screen
        screen = pag.screenshot()
        # wait to see if the grayed out 'Next' button appears
        if pag.pixelMatchesColor(*coords[buy_sell_name_mapping[nt.group_name_length]], sell_something_button_mouseover):
            mouse_click(buy_sell_name_mapping[nt.group_name_length])
            return wait_for_buy_sell_to_load(nt)
        print('pixel {} coords {} matching {} actual {}'.format(coords[buy_sell_name_mapping[nt.group_name_length]], sell_something_button_mouseover, True, screen.getpixel(coords[buy_sell_name_mapping[nt.group_name_length]])))
        count += 1
        if count > 120:
            return False

# refactor one: one function running a while loop waiting on pixels scrolling clicking etc
def run_buy_sell_group(nt):
    print(nt)
    mouse_click('menu')
    keyboard('Chrome')
    mouse_click('chrome')
    if not wait_for_screen_or_clean_up('url_bar', chrome_url_bar_color):
        return
    open_tab(nt.group_link)
    press('ctrl', 't')
    open_tab(nt.google_drive_link)
    press('ctrl', 'pageup') # back to facebook tab
    sleep(2)

# open the sell something window and wait for it to load
    if not wait_for_screen_or_clean_up(buy_sell_name_mapping[nt.group_name_length],
                                sell_something_button_mouseover,
                                True,
                                lambda : [
                                    move_to(buy_sell_name_mapping[nt.group_name_length]),
                                    pag.moveRel(200, 200, .1),
                                    pag.moveRel(-200, -200, .1),
                                    pag.scroll(1000), ]):
        return
    mouse_click(buy_sell_name_mapping[nt.group_name_length])
    if not wait_for_screen_or_clean_up('gray_next_that_shows_window_is_open',
                                   buy_sell_window_open_color,
                                   True,
                                   lambda : pag.scroll(1000)):
        return

    # Populate the condition
    if not wait_for_screen_or_clean_up('new_condition',
                                   new_condition_color,
                                   True,
                                   lambda : [
                                        mouse_click('condition_selection'),
                                        move_to('new_condition'),
                                        pag.moveRel(200, 200, .1),
                                        pag.moveRel(-200, -200, .1), sleep(1)]):
        return
    mouse_click('new_condition')
    # Populate the title, price from the named tuple
    copy_paste(nt.title, 'title')
    copy_paste(nt.price, 'price')
    press('ctrl', 'pagedown') # to google doc
    #mouse_click('tab_two')
    if not wait_for_screen_or_clean_up('google_drive_ready', drive_ready_color):
        return
    mouse_click('google_drive_ready')
    press('ctrl', 'a') # select the text
    sleep(1)
    press('ctrl', 'c') # copy the text
    sleep(1)
    press('ctrl', 'pageup') # back to facebook
    sleep(1)
    mouse_click('description')
    press('ctrl', 'v')

    # upload the photos
    if not wait_for_screen_or_clean_up('open_files_bar',
                                       open_file_color,
                                       True,
                                       lambda : mouse_click('add_photos')):
        return
    copy_paste(nt.folder_path, 'file_upload_path')
    sleep(1)
    press('backspace')
    press('enter')
    sleep(1)
    # select all photos and go
    press('ctrl', 'a')
    press('enter')
    sleep(2) # takes some time to upload the photos

    # now we'll scroll down to the bottom of the sc
    if not wait_for_screen_or_clean_up('blue_next',
                                       [facebook_ready_to_post_color, facebook_ready_to_post_alt_color], # mouseover changes color
                                       True,
                                       lambda : pag.scroll(-1000)): # scroll down
        return
    mouse_click('blue_next')
# same func to scroll down past the list of other buy sell groups
    if not wait_for_screen_or_clean_up('blue_next',
                                       [facebook_ready_to_post_color, facebook_ready_to_post_alt_color],
                                       True,
                                       lambda : pag.scroll(-1000)): # scroll down
        return
    mouse_click('blue_next')
    if not wait_for_screen_or_clean_up('blue_next', buy_sell_post_pending_color, False): # wait for the gray button to disappear
        return
    sleep(4)
    clean_up()

#def run_group(google_doc_link, folder_path, group_tup, post_coords):
def run_group(nt): #google_doc_link, folder_path, group_tup, post_coords):
    mouse_click('menu')
    keyboard('Chrome')
    sleep(2) # TODO: wait for screen
    mouse_click('chrome')
    if not wait_for_screen_or_clean_up('url_bar', chrome_url_bar_color):
        return
    open_tab(nt.group_link)
    press('ctrl', 't')
    open_tab(nt.google_drive_link)
    press('ctrl', 'pageup') # back to facebook tab
    if not wait_for_screen_or_clean_up('open_files_bar', # loc on screen
                             open_file_color,
                             True,
                             lambda : [move_to(group_name_mapping[nt.group_name_length]),
                                pag.scroll(1000),
                                mouse_click(group_name_mapping[nt.group_name_length])]):
        return
    copy_paste(nt.folder_path, 'file_upload_path')
    sleep(1)
    press('backspace')
    press('enter')
    sleep(1)
    # select all photos and go
    press('ctrl', 'a')
    press('enter')
    sleep(2) # takes some time to upload the photos

    press('ctrl', 'pagedown') # to google doc
    if not wait_for_screen_or_clean_up('google_drive_ready', drive_ready_color):
        return
    mouse_click('google_drive_ready')
    press('ctrl', 'a') # select the text
    sleep(1)
    press('ctrl', 'c') # copy the text
    sleep(1)
    press('ctrl', 'pageup') # back to facebook
    #mouse_click('tab_one')
    sleep(1)
    mouse_click('write_something')
    press('ctrl', 'v')
    if not wait_for_screen_or_clean_up(nt.post_button_coords, facebook_ready_to_post_color):
        return
    pag.click(*(nt.post_button_coords))
    sleep(5)

    if not wait_for_screen_or_clean_up(nt.post_pending_coords, facebook_post_pending_color, False):
        return
    sleep(1)
    clean_up()

if __name__=='__main__':
    schools = ['USC']
    selections = ['buy_sell', 'group']

    # Set the util class to use the coordinates of facebook buttons
    init(coords)

    if 'buy_sell' in selections:
        for data in all_buy_sells:
            if data.short_name in schools:
                run_buy_sell_group(data)
            else:
                print('Skipping {}'.format(data.short_name))
    else:
        print('Skipping buy_sell')
    if 'group' in selections:
        for data in all_groups:
            if data.short_name in schools:
                run_group(data)
            else:
                print('Skipping {}'.format(data.short_name))
    else:
        print('Skipping normal groups')

