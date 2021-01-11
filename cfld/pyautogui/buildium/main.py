from utils import *
from buildium.buildium_constants import coords, colors
import sys

def open_buildium():
    open_chrome()
    keyboard('https://cleanfloorsandlockingdoorsinc.managebuilding.com/Manager/app/homepage/dashboard?initpage=1')
    press('enter')

    # Will trigger if we need to log in
    if wait_for_screen_or_clean_up('login_background', 'already logged in', timeout_seconds = 10, clean_func = lambda : None):
        wait_for_screen_then_click_or_exit('login_with_google', 'could not locate login with google button')
        wait_for_screen_then_click_or_exit('login_as_tyler_icon', 'could not locate green tyler@cf-ld.com icon')

    wait_for_screen_or_exit('homepage', 'buildium homepage not loaded')
    print('buildium opened successfully')

def open_applicant(args):
    open_buildium()
    wait_for_screen_then_click_or_exit('leasing', 'failed to open buildium leasing tab')
    wait_for_screen_then_click_or_exit('applicants', 'failed to open buildium applicants tab',
                                x = lambda : [
                                    move_to('applicants'),
                                    pag.moveRel(1, 1, .1),
                                    pag.moveRel(-1, -1, .1)])

    # We might already have a filter, in which case we remove it
    if wait_for_screen_or_clean_up('clear_existing_filter', 'error while clearing existing filter', timeout_seconds = 30, 
                                x = lambda : [
                                    move_to('clear_existing_filter'),
                                    pag.moveRel(1, 1, .1),
                                    pag.moveRel(-1, -1, .1)],
                                clean_func = lambda : None):
        mouse_click('clear_existing_filter')

    wait_for_screen_then_click_or_exit('add_filter_option', 'failed to open filter option',
                                x = lambda : [
                                    move_to('add_filter_option'),
                                    pag.moveRel(1, 1, .1),
                                    pag.moveRel(-1, -1, .1)])

    wait_for_screen_then_click_or_exit('filter_by_applicant', 'failed to click on applicant under add filter option dropdown',
                                x = lambda : [
                                    move_to('filter_by_applicant'),
                                    pag.moveRel(1, 1, .1),
                                    pag.moveRel(-1, -1, .1)])
    sleep(1)
    keyboard(first)
    keyboard(' ')
    keyboard(last)
    press('enter')
    sleep(1)
    wait_for_screen_then_click_or_exit('applicant_row', 'failed to find applicant name',
                                x = lambda : [
                                    move_to('applicant_row'),
                                    pag.moveRel(1, 1, .1),
                                    pag.moveRel(-1, -1, .1)])

# return a list of file names that we saved the screenshots in
def take_screenshots(first, last, start_fn_index = 0):
    clicks = coords['scroll_click_count']
    
    count = start_fn_index
    extension = '.png'
    base_fn = '{}_{}'.format(first, last)
    folder = '/home/tgaldes/Pictures/'
    breaking = False
    fns = []
    while True: # TODO: look for bar in lower right corner all the way at the bottom
        screen = pag.screenshot()
        fn = folder + base_fn + '_' + str(count) + extension
        screen.save(fn)
        fns.append(fn)
        count += 1
        for i in range(clicks):
            mouse_click('bottom_right_down_button')
        if breaking:
            break
        if wait_for_screen_or_clean_up('bottom_right', 'still not done taking screenshots', clean_func = lambda : None, timeout_seconds = 1):
            breaking = True
        elif wait_for_screen_or_clean_up('no_bottom_right_scroll_bar', 'there is a scroll bar', clean_func = lambda : None, timeout_seconds = 1):
            break
    return fns

def get_screening(first, last):
    #open_applicant(first, last)
    sleep(2)
    wait_for_screen_then_click_or_exit('tenant_screening', 'could not click on first screening button',
                                x = lambda : [
                                    move_to('tenant_screening'),
                                    pag.moveRel(1, 1, .1),
                                    pag.moveRel(-1, -1, .1)])

    sleep(5)
    start_fn_index = 0
    all_fns = []
    for page_link, page in [('credit_report_link', 'credit_report'), ('criminal_report_link', 'criminal_report'), ('evictions_report_link', 'evictions_report')]:
        # load the landing page
        wait_for_screen_or_exit('move_in', 'could not load page with credit screening',
                                    x = lambda : [
                                        move_to('move_in'),
                                        pag.moveRel(1, 1, .1),
                                        pag.moveRel(-1, -1, .1)])
        # click on the page we want
        mouse_click(page_link)
        # let that page load (look for light blue areas)
        wait_for_screen_or_exit(page, 'could not load {}'.format(page),
                                    x = lambda : [
                                        move_to(page),
                                        pag.moveRel(1, 1, .1),
                                        pag.moveRel(-1, -1, .1)])
        fns = take_screenshots(first, last, start_fn_index)
        all_fns.extend(fns)
        start_fn_index += len(fns)
        print(all_fns)
        mouse_click('back_on_browser')
    print(all_fns)
    return all_fns


    


def process_application(first, last):
    open_applicant(first, last)
    # Charge their credit card
    wait_for_screen_then_click_or_exit('process_fee', 'failed to find process fee button at start of credit card screening',
                                x = lambda : [
                                    move_to('process_fee'),
                                    pag.moveRel(1, 1, .1),
                                    pag.moveRel(-1, -1, .1)])
    wait_for_screen_then_click_or_exit('green_process_fee', 'failed to find green process fee button before charging credit card',
                                x = lambda : [
                                    move_to('green_process_fee'),
                                    pag.moveRel(1, 1, .1),
                                    pag.moveRel(-1, -1, .1)])
    # Now we expect the charge to be pending
    wait_for_screen_or_clean_up('pending_process_fee', timeout_seconds = 30, 
                                clean_func = lambda : None)

    # Do the screening
    wait_for_screen_then_click_or_exit('tenant_screening', 'could not click on first screening button',
                                x = lambda : [
                                    move_to('tenant_screening'),
                                    pag.moveRel(1, 1, .1),
                                    pag.moveRel(-1, -1, .1)])
    wait_for_screen_then_click_or_exit('green_tenant_screening', 'could not click on second screening button',
                                x = lambda : [
                                    move_to('green_tenant_screening'),
                                    pag.moveRel(1, 1, .1),
                                    pag.moveRel(-1, -1, .1)])
    # Now let the page load
    wait_for_screen_or_exit('green_review_order', 'never found green review order button before entering in rent and deposit values',
                                x = lambda : [
                                    move_to('green_review_order'),
                                    pag.moveRel(1, 1, .1),
                                    pag.moveRel(-1, -1, .1)])
    mouse_click('monthly_rent')
    keyboard('900')
    mouse_click('security_deposit')
    keyboard('900')

    mouse_click('charge_my_buildium_account')
    wait_for_screen_or_exit('charge_my_buildium_account', 'failed to click on charge my buildium account')
    wait_for_screen_then_click_or_exit('green_review_order', 'failed to click on review order button',
                                x = lambda : [
                                    move_to('green_review_order'),
                                    pag.moveRel(1, 1, .1),
                                    pag.moveRel(-1, -1, .1)])
    # Now let the page load
    wait_for_screen_or_exit('place_order', 'final confirm credit check screen didn\'t load',
                                x = lambda : [
                                    move_to('place_order'),
                                    pag.moveRel(1, 1, .1),
                                    pag.moveRel(-1, -1, .1)])

    mouse_click('authorize_charge')
    wait_for_screen_or_exit('authorize_charge', 'never found button to authorize charge',
                                x = lambda : [
                                    move_to('authorize_charge'),
                                    pag.moveRel(1, 1, .1),
                                    pag.moveRel(-1, -1, .1)])
    wait_for_screen_then_click_or_exit('place_order', 'failed while attempting to click on place order',
                                x = lambda : [
                                    move_to('place_order'),
                                    pag.moveRel(1, 1, .1),
                                    pag.moveRel(-1, -1, .1)])



if __name__=='__main__':
    if len(sys.argv) < 3:
        print('No first and last name passed to process_application.')
        exit(1)
    first, last = sys.argv[1], sys.argv[2]

    init(coords, colors) # give constants to utils
    
    #process_application(first, last)
    #take_screenshots(first, last)
    get_screening(first, last)
