# written by Roberto Franzosi October 2019, edited Spring 2020


# RUN section ______________________________________________________________________________________________________________________________________________________


def run():
    print("Exit")


# # the values of the GUI widgets MUST be entered in the command otherwise they will not be updated


# # GUI section ______________________________________________________________________________________________________________________________________________________

# # the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
# #   just change the next statement to True or False IO_setup_display_brief=True

# GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
#                              increment=2)  # to be added for full display

# # The 4 values of config_option refer to:
# #   input file
#         # 1 for CoNLL file
#         # 2 for TXT file
#         # 3 for csv file
#         # 4 for any type of file
#         # 5 for txt or html
#         # 6 for txt or csv
# #   input dir
# #   input secondary dir
# #   output dir


# #setup GUI widgets


# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
#                                    open_CoNLL_search_GUI_button,
#                                    False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
#                                    "Click on the button to open the GUI")


# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
#                                    open_file_search_GUI_button,
#                                    False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
#                                    "Click on the button to open the GUI")

# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
#                                    open_nGram_VIEWER_search_GUI_button,
#                                    False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
#                                    "Click on the button to open the GUI")

# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
#                                    open_word_sense_search_GUI_button,
#                                    False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
#                                    "Click on the button to open the GUI")

# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
#                                    open_word_distance_search_GUI_button,
#                                    False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
#                                    "Click on the button to open the GUI")

# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
#                                    open_WordNet_search_GUI_button,
#                                    False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
#                                    "Click on the button to open the GUI")

# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
#                                    open_word_search_GUI_button,
#                                    False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
#                                    "Click on the button to open the GUI")
# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
#                                    export_csv_field_GUI_button,
#                                    False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
#                                    "Click on the button to open the GUI")


# # add all the lines to the end to every special GUI
# # change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# # any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
# def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
#     y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer, "NLP Suite Help",
#                               "Please, click on the button to open the GUI for exporting the content of csv field(s) to a text or csv file.\n\nYou can use this option, for instance, to export all the sentences extracted via any of the searches to a txt file for further analysis.")

# # change the value of the readMe_message
