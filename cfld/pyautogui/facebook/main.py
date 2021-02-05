import pdb
import pyautogui as pag
pag.PAUSE = 1
pag.FAILSAFE = True
from time import sleep
import os
import sys

from facebook.inputs import all_groups, all_buy_sells
from facebook.facebook_constants import * # TODO refactor three
from utils import *



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

def open_facebook():
    open_chrome()
    keyboard('https://www.facebook.com/marketplace/you')
    press('enter')
    wait_for_screen_or_clean_up('facebook_homepage', 'failed_to_load_facebook_homepage')

# TODO: if the last message was from us, just close the window
# TODO: type my response slower
def answer_via_facebook_messenger(params):
    response = params[0]
    open_facebook()
    default_response_substrings = ['still available', 'interested in', 'condition is', 'you deliver']
    # open facebook
    sent_responses = 0
    # while we have a message aka gray bubble
    while wait_for_screen_or_clean_up('incoming_message', 'no incoming messages found', timeout_seconds=10):
        # grab the text
        mouse_click('incoming_message', n=3)
        incoming_message = copy().lower()
        # see if any of the default repsonses are populated in it
        for default_response_substring in default_response_substrings:
            if default_response_substring in incoming_message:
                # send our own default response specified as an argument
                mouse_click('reply_window')
                keyboard(response)
                press('enter')
                # close the chat
                wait_for_screen_then_click_or_exit('close_chat', 'couldnt close chat window after sending message',
                    x = lambda : [
                        move_to('close_chat'),
                        pag.moveRel(1, 1, .1),
                        pag.moveRel(-1, -1, .1)])
                sent_responses += 1
                break
    print('Sent {} responses.'.format(sent_responses))
    return sent_responses


def delete_post():
    while True:
        if not wait_for_screen_then_click('first_delete_button', # loc on screen
                                'failed while clicking first_delete_button',
                                ['first_delete_button', 'first_delete_button_alt'],
                                 x = lambda : [
                                        move_to('first_delete_button'),
                                        pag.moveRel(1, 1, .1),
                                        pag.moveRel(-1, -1, .1)]):
            return False
        sleep(3)
        if not wait_for_screen_then_click('delete_post', # loc on screen
                                'failed while clicking delete_post',
                                 x = lambda : [
                                        move_to('delete_post'),
                                        pag.moveRel(1, 1, .1),
                                        pag.moveRel(-1, -1, .1)]):
            continue # Try again from step one
        if not wait_for_screen_then_click('confirm_delete', # loc on screen
                                'failed while clicking confirm_delete',
                                ['confirm_delete', 'confirm_delete_alt'],
                                 x = lambda : [
                                        move_to('confirm_delete'),
                                        pag.moveRel(1, 1, .1),
                                        pag.moveRel(-1, -1, .1)]):
            return False
        return True

# deletes active posts
def delete_active_post():
    while True:
        sleep(1)
        mouse_click('active_first_delete_button')
        sleep(3)
        if not wait_for_screen_then_click('active_delete_post', # loc on screen
                                'failed while clicking delete_post',
                                timeout_seconds=10,
                                 x = lambda : [
                                        move_to('active_delete_post'),
                                        pag.moveRel(1, 1, .1),
                                        pag.moveRel(-1, -1, .1)]):
            if not wait_for_screen_then_click('active_delete_post_alt', # loc on screen
                                    'failed while clicking delete_post',
                                     x = lambda : [
                                            move_to('active_delete_post_alt'),
                                            pag.moveRel(1, 1, .1),
                                            pag.moveRel(-1, -1, .1)]):
                continue # Try again from step one
        if not wait_for_screen_then_click('active_confirm_delete', # loc on screen
                                'failed while clicking confirm_delete',
                                ['active_confirm_delete', 'active_confirm_delete_alt'],
                                 x = lambda : [
                                        move_to('active_confirm_delete'),
                                        pag.moveRel(1, 1, .1),
                                        pag.moveRel(-1, -1, .1)]):
            return False
        return True

# for now assumes that we'll open the marketplace page manually
def delete_posts(active=False):
    count = 0
    if active:
        f = delete_active_post
    else:
        f = delete_post
    while f():
        count += 1
        sleep(7) # let facebook remove the one we deleted from the screen
    print('Deleted {} posts.'.format(count))
    

if __name__=='__main__':
    # Set the util class to use the coordinates of facebook buttons
    init(application_coords, application_colors)

    if len(sys.argv) < 2:
        print('need to specify desired function and arguments to that function')
        exit(1)
    if len(sys.argv) == 2:
        function = sys.argv[1]
    else:
        function, params = sys.argv[1], sys.argv[2:]

    if function == 'messenger':
        answer_via_facebook_messenger(params)
    elif function == 'delete':
        sleep(2)
        delete_posts()
    elif function == 'delete_active':
        sleep(2)
        delete_posts(True)
    elif function == 'post':
        schools = ['USC']
        selections = ['buy_sell', 'group']


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

