# hold corrdinates of various clicks we need in a map so that we can run indep of display
group_name_mapping = {1 : 'one_line_group_photo_video', 
                      2 : 'two_line_group_photo_video',
                      3 : 'three_line_group_photo_video'}
buy_sell_name_mapping = {1 : 'one_line_sell_something', 
                      2 : 'two_line_sell_something',
                      3 : 'three_line_sell_something'}
                      
all_coords = {
    'l' : # laptop 
        { 'menu' : (100, 100) },
    'm' : # monitor
        { 
# ubuntu
            'menu' : (23, 65),
            'chrome' : (168, 170),
# chrome
            'close_chrome' : (91, 46),
            'url_bar' : (562, 78),
            'tab_one' : (264, 60),
            'tab_two' : (540, 60),
            'open_files_bar' : (800, 225),
# normal group
            'file_upload_path' : (1202, 250),
            'write_something' : (1144, 590),
            'one_line_group_photo_video' : (956, 786),
            'two_line_group_photo_video' : (956, 820),
            'three_line_group_photo_video' : (956, 853),
# buy and sell group
            'one_line_sell_something' : (1238, 737),
            'two_line_sell_something' : (1238, 768),
            'three_line_sell_something' : (1238, 810),
            'add_photos' : (1111, 438),
            'title' : (1121, 643),
            'price' : (1121, 718),
            'description' : (1121, 891),
            'gray_next_that_shows_window_is_open' : (1411, 1316),
            'blue_next' : (1169, 1486),
# drive
            'google_drive_ready' : (949, 286),
            'new_condition' : (1346, 847),
            'condition_selection' : (1292, 802),

# general facebook
            'facebook_homepage' : (95, 130),
# responding via messenger
            'incoming_message' : (2314, 1312),
            'close_chat' : (2437, 1062),
            'reply_window' : (2315, 1570),

# deleting posts
            'first_delete_button' : (672, 494),
            'delete_post' : (693, 870),
            'confirm_delete' : (1535, 888),
# deleting active posts
            'active_first_delete_button' : (1058, 430),
            'active_delete_post' : (1117, 844),
            'active_delete_post_alt' : (1074, 882), # for active posts marked as sold
            'active_confirm_delete' : (1553, 888)
        }
    }
mkey = 'm' # TODO
application_coords = all_coords[mkey]

# colors that we want to wait for on screen 
# TODO: refactor these colors to a map
facebook_post_pending_color = (246, 246, 246)
facebook_post_photo_video_color = (122, 183, 103) # green in the button
facebook_post_photo_video_color_bk = (116, 173, 98) # green in the button
facebook_ready_to_post_color = (72, 123, 237) # blue
facebook_ready_to_post_alt_color = (69, 117, 225) # blue
drive_ready_color = (255, 255, 255)
chrome_url_bar_color = (255, 255, 255)
open_file_color = (71, 70, 64)
buy_sell_post_pending_color = (229, 230, 235)
buy_sell_window_open_color = (229, 230, 235)
sell_something_button_mouseover = (217, 218, 223)
new_condition_color = (242, 242, 242)


application_colors = {
    'incoming_message' : (229, 230, 235),
    'close_chat' : (244, 244, 244),
    'facebook_homepage' : (88, 150, 240),

# deleting posts
    'first_delete_button' : (217, 218, 223),
    'first_delete_button_alt' : (217, 217, 224),
    'delete_post' : (242, 242, 242),
    'confirm_delete' : (69, 117, 225),
    'confirm_delete_alt' : (81, 30, 235),
# deleting active posts
    'active_first_delete_button' : (217, 218, 223),
    'active_first_delete_button_alt' : (217, 217, 224),
    'active_delete_post' : (217, 218, 223),
    'active_delete_post_alt' : (217, 218, 223),
    'active_confirm_delete' : (69, 117, 225),
    'active_confirm_delete_alt' : (81, 30, 235)
}









# Refactor duplicates
