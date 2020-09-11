import pyautogui as pag
import pdb
from time import sleep
from constants import * # TODO refactor three
import os

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
    sleep(.2)
    # copy
    os.system('cat {} | xclip -selection clipboard'.format(fn))
    # select dest
    mouse_click(dest)
    # paste
    press('ctrl', 'v')
    sleep(.2)

def open_tab(url):
    copy_paste(url, 'url_bar')
    sleep(1)
    mouse_click('url_bar')
    press('enter')

def clean_up():
    press('ctrl', 'w')
    press('ctrl', 'w')
    mouse_click('close_chrome')

# return True on match/no match, false if we timed out
def wait_for_screen_general(loc_on_screen, # a string that we look up in coords, or a tuple in form (x, y)
                            target_color, # the color we will be looking for at loc_on_screen
                            match = True, # True -> return when loc_on_screen matches target_color, False -> return when they don't match
                            callback = lambda : None, # function we will run each time before we check the pixel match
                            timeout_seconds = 120,
                            ):
    if type(loc_on_screen) == str:
        x, y = coords[loc_on_screen]
    else:
        x, y = loc_on_screen
    count = 0
    sleep(.2)
    while True:
        callback() # run caller supplied callback (e.g. try scrolling up and clicking)
        sleep(1)
        screen = pag.screenshot()
        if type(target_color) == list:
            for color in target_color:
                if match == pag.pixelMatchesColor(x, y, color):
                    return True
        else:
            if match == pag.pixelMatchesColor(x, y, target_color):
                return True
        print('location on screen ({}, {}), actual: {}, target: {}, matching colors: {}'.format(x, y, screen.getpixel((x, y)), target_color, match))
        if count > timeout_seconds:
            print('Timed out after {} seconds'.format(count))
            return False
        count += 1

# if we time out, run the supplied clean up func and exit
def wait_for_screen_or_clean_up(loc_on_screen, target_color, match = True, x = lambda : None, timeout_seconds = 120, clean_func = clean_up):
    res = wait_for_screen_general(loc_on_screen, target_color, match, x, timeout_seconds)
    if res:
        return True
    clean_up()
    return False
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

# if we time out, print a message and exit
def wait_for_screen_or_exit(loc_on_screen, target_color, match = True, x = lambda : None, timeout_seconds = 120):
    res = wait_for_screen_general(loc_on_screen, target_color, match, x, timeout_seconds)
    if res:
        return True
    print('wait_for_screen returned false, exiting.')
    print('Goodbye :)')
    exit(1)
