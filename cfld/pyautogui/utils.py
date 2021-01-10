import pyautogui as pag
import pdb
from time import sleep
import os
from constants import coords, colors

def init(constant_coords, constant_colors):
    global application_coords
    application_coords = constant_coords
    global application_colors
    application_colors = constant_colors

def mouse_click(item, sleep_secs=0):
    if item in application_coords:
        pag.click(*application_coords[item])
    else:
        pag.click(*coords[item])

    sleep(sleep_secs)
    pass
def move_to(item):
    if item in application_coords:
        pag.moveTo(*application_coords[item])
    else:
        pag.click(*coords[item])
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
def wait_for_screen_general(loc_on_screen, # a string that we look up in application_coords, or a tuple in form (x, y)
                            target_color, # the color we will be looking for at loc_on_screen (coords or a list of coords)
                            match = True, # True -> return when loc_on_screen matches target_color, False -> return when they don't match
                            callback = lambda : None, # function we will run each time before we check the pixel match
                            timeout_seconds = 120,
                            ):
    if type(loc_on_screen) == str:
        if loc_on_screen in application_coords:
            x, y = application_coords[loc_on_screen]
        else:
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

def get_target_colors(loc_on_screen_name, target_color_names=[]):
    inner_tc_names = []
    if not target_color_names:
        inner_tc_names.append(loc_on_screen_name)
    else:
        for item in target_color_names:
            inner_tc_names.append(item)
    target_colors = []
    for target_color_name in inner_tc_names:
        if target_color_name in application_colors:
            target_colors.append(application_colors[target_color_name])
        else:
            target_colors.append(colors[target_color_name])
    return target_colors

# if we time out, run the supplied clean up func and exit
def wait_for_screen_or_clean_up(loc_on_screen_name, error_msg, target_color_names=[], match = True, x = lambda : None, timeout_seconds = 120, clean_func = clean_up):
    tcs = get_target_colors(loc_on_screen_name, target_color_names)
    res = wait_for_screen_general(loc_on_screen_name, tcs, match, x, timeout_seconds)
    if res:
        return True
    print(error_msg)
    clean_func()
    return False


# if we time out, print a message and exit
def wait_for_screen_or_exit(loc_on_screen_name, error_msg, target_color_names=[], match = True, x = lambda : None, timeout_seconds = 120):
    tcs = get_target_colors(loc_on_screen_name, target_color_names)
    res = wait_for_screen_general(loc_on_screen_name, tcs, match, x, timeout_seconds)
    if res:
        return True
    print(error_msg)
    exit(1)

def wait_for_screen_then_click_or_exit(loc_on_screen_name, error_msg, target_color_names=[], match = True, x = lambda : None, timeout_seconds = 120, clean_func = clean_up):
    tcs = get_target_colors(loc_on_screen_name, target_color_names)
    res = wait_for_screen_general(loc_on_screen_name, tcs, match, x, timeout_seconds)
    if res:
        mouse_click(loc_on_screen_name)
        return True
    print(error_msg)
    exit(1)

# Open chrome and click on the url bar
def open_chrome():
    mouse_click('menu')
    keyboard('Chrome')
    wait_for_screen_then_click_or_exit('chrome_icon_in_linux_menu', 'chrome did not pop up from linux menu.')
    wait_for_screen_then_click_or_exit('url_bar', 'url_bar did not pop up from chrome', target_color_names=['url_bar', 'url_bar_gray_color', 'url_bar_dark_color'])
    
