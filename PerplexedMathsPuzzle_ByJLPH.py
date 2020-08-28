import tkinter
import random
import numpy
import os
import sys
import copy
import threading


game_windows = tkinter.Tk()
game_windows.title("Perplexed Maths Puzzle By JohnnyLPH")
game_windows.configure(bg="#65E1D6")

common_frame_color = "#A0FBF4"
common_button_color = "#A9F5F2"

mode_frame = tkinter.LabelFrame(game_windows, text="Game Mode", bg=common_frame_color)  # Show settings menu.
mode_frame.grid(row=0, column=0, padx=10, pady=10, sticky="e")

info_frame = tkinter.LabelFrame(game_windows, text="Game Info", bg=common_frame_color)  # Show info about the game.
info_frame.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky="news")


num_of_row = tkinter.IntVar()  # Total rows.
num_of_col = tkinter.IntVar()  # Total columns.

range_value = tkinter.IntVar()  # Range of options, determine how the difficult is the puzzle.
with_negatives = tkinter.StringVar()  # Include negative options makes the puzzle harder to solve.


def get_game_settings():  # Get all settings required to create the puzzle later.
    num_of_row.set(3)  # Default number of rows = 3.
    num_of_col.set(3)  # Default number of columns = 3.
    range_value.set(10)  # Default range of options = 10.
    with_negatives.set("Yes")  # Default = Include negative options.

    def reset_game():  # Pressed Reset Game button.
        os.execl(sys.executable, sys.executable, *sys.argv)  # Re-execute the whole script.
        return

    def start_game():  # Pressed Start Game button. Prevent player from changing any setting from now on.
        get_num_row_info.configure(state="disabled")
        get_num_col_info.configure(state="disabled")
        get_range_value_info.configure(state="disabled")
        get_negatives_option_info.configure(state="disabled")

        get_num_row.configure(state="disabled", relief="flat", bg=common_frame_color)
        get_num_col.configure(state="disabled", relief="flat", bg=common_frame_color)
        get_range_value.configure(state="disabled", relief="flat", bg=common_frame_color)
        get_negatives_option.configure(state="disabled", relief="flat", bg=common_frame_color)

        start_game_button.configure(state="disabled", relief="flat", bg=common_frame_color)
        reset_game_button.configure(state="normal", bg="red", fg="#FFFF00", relief="raised", command=reset_game,
                                    activebackground=common_frame_color)

        prepare_settings()  # Prepare the puzzle.
        return

    get_num_row_info = tkinter.Label(mode_frame, text="Number Of Rows =", bg=common_frame_color)
    get_num_row = tkinter.OptionMenu(mode_frame, num_of_row, 3, 4, 5, 6, 7, 8, 9, 10)  # Min = 3, Max = 10.
    get_num_row.configure(highlightbackground=common_frame_color, bg=common_button_color)

    get_num_col_info = tkinter.Label(mode_frame, text="Number Of Columns =", bg=common_frame_color)
    get_num_col = tkinter.OptionMenu(mode_frame, num_of_col, 3, 4, 5, 6, 7, 8, 9, 10)  # Min = 3, Max = 10.
    get_num_col.configure(highlightbackground=common_frame_color, bg=common_button_color)

    get_range_value_info = tkinter.Label(mode_frame, text="Range Of Options =", bg=common_frame_color)
    get_range_value = tkinter.OptionMenu(mode_frame, range_value, 10, 50, 100, 500, 1000, 5000, 10000)  # Max = 10000.
    get_range_value.configure(highlightbackground=common_frame_color, bg=common_button_color)

    get_negatives_option_info = tkinter.Label(mode_frame, text="With Negative Options =", bg=common_frame_color)
    get_negatives_option = tkinter.OptionMenu(mode_frame, with_negatives, "Yes", "No")
    get_negatives_option.configure(width=5, highlightbackground=common_frame_color, bg=common_button_color)

    start_game_button = tkinter.Button(mode_frame, text="Start Game", bg="#99FF00", command=start_game)
    start_game_button.configure(activebackground=common_frame_color)
    reset_game_button = tkinter.Button(mode_frame, text="Reset Game", state="disabled", relief="flat",
                                       bg=common_frame_color)

    get_num_row_info.grid(row=0, column=0, sticky="e")
    get_num_col_info.grid(row=1, column=0, sticky="e")
    get_range_value_info.grid(row=2, column=0, sticky="e")
    get_negatives_option_info.grid(row=3, column=0, sticky="e")

    get_num_row.grid(row=0, column=1, sticky="ew")
    get_num_col.grid(row=1, column=1, sticky="ew")
    get_range_value.grid(row=2, column=1, sticky="ew")
    get_negatives_option.grid(row=3, column=1, sticky="ew")

    start_game_button.grid(row=4, column=0, columnspan=2, padx=3, pady=3, sticky="ew")
    reset_game_button.grid(row=5, column=0, columnspan=2, padx=3, pady=3, sticky="ew")

    info_1_text = "- Arrange the options until the sum of each row or column is equal to the respective answer."
    info_1 = tkinter.Label(info_frame, text=info_1_text, bg=common_frame_color)
    info_1.grid(row=0, column=0, sticky="w")

    info_2_text = "- The answer block will turn blue if the sum of options matches the answer."
    info_2 = tkinter.Label(info_frame, text=info_2_text, bg=common_frame_color)
    info_2.grid(row=1, column=0, sticky="w")

    info_3_text = "- The puzzle is solved when all answers are matched."
    info_3 = tkinter.Label(info_frame, text=info_3_text, bg=common_frame_color)
    info_3.grid(row=2, column=0, sticky="w")
    return


game_frame_color = "#1CEFAB"
game_frame = tkinter.LabelFrame(game_windows, text="Puzzle Board", relief="raised", bd=3, bg=game_frame_color)

game_grid = []
game_solution = []
row_ans = []  # Top to Bottom
col_ans = []  # Left to Right


def prepare_settings():  # Create the puzzle with specific settings.
    global game_grid
    global game_solution
    global row_ans
    global col_ans

    option_list = []  # Temporarily store options.

    # Number of unique options [Duplicates Removed] = complexity.
    complexity = random.randint(num_of_row.get() + num_of_col.get(), num_of_row.get() * num_of_col.get())

    # Complexity shouldn't be higher than the range of options. Do checking.
    if with_negatives.get() == "Yes":
        if complexity > range_value.get() * 2:
            complexity = random.randint(range_value.get(), range_value.get() * 2)
    else:
        if complexity > range_value.get():
            complexity = random.randint(range_value.get() / 2, range_value.get())

    # Find a number of unique options and also make sure the option list isn't over the maximum size.
    while len(list(set(option_list))) < complexity and len(option_list) < num_of_row.get() * num_of_col.get():
        if with_negatives.get() == "Yes":
            random_option = random.randint(-range_value.get(), range_value.get())
        else:
            random_option = random.randint(0, range_value.get())

        if len(option_list) == 0 or random_option not in option_list:
            option_list.append(random_option)

    # Fill the option list till maximum size.
    while len(option_list) < num_of_row.get() * num_of_col.get():
        option_list.append(random.choice(option_list))

    inner_use_option_list = copy.deepcopy(option_list)  # Make a copy of option list for generating solution.

    # Generate a random solution before shuffling all options to make a puzzle.
    for row in range(num_of_row.get()):
        row_list = []
        for col in range(num_of_col.get()):
            current_option = random.choice(inner_use_option_list)
            row_list.append(current_option)

            del inner_use_option_list[inner_use_option_list.index(current_option)]

        game_solution.append(row_list)

    game_solution = numpy.array(game_solution)  # Convert from normal list to numpy array.

    # Calculate each row answer from the previously generated game solution.
    for row in range(num_of_row.get()):
        row_ans.append(numpy.sum(game_solution[row]))

    # Calculate each column answer from the previously generated game solution.
    for col in range(num_of_col.get()):
        total_sum = 0
        for row in range(num_of_row.get()):
            total_sum += game_solution[row, col]
        col_ans.append(total_sum)

    inner_use_option_list = copy.deepcopy(option_list)  # Make another copy of option list for creating game grid.

    # Generate a random game grid [Puzzle] for solving.
    while True:
        game_grid = []

        for row in range(num_of_row.get()):
            row_list = []
            for col in range(num_of_col.get()):
                current_option = random.choice(inner_use_option_list)
                row_list.append(current_option)

                del inner_use_option_list[inner_use_option_list.index(current_option)]

            game_grid.append(row_list)

        if game_grid == game_solution.tolist():  # Same as solution, game grid cannot be accepted.
            continue

        game_grid = numpy.array(game_grid)  # Convert from normal list to numpy array.
        break

    game_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="n")  # Display the game frame.

    thread1 = threading.Thread(target=update_answer_frame, args=(True,))  # First call, True.
    thread2 = threading.Thread(target=update_game_grid, args=(True,))  # First call, True.
    thread1.start()
    thread2.start()
    return


# Store the indexes of achieved answers.
row_ans_index_list = []
col_ans_index_list = []
# Store the current sums of rows and columns.
current_all_row_ans = []
current_all_col_ans = []


def update_answer_frame(first_call):  # Display all row answers and column answers.
    global row_ans_index_list
    global col_ans_index_list
    global current_all_row_ans
    global current_all_col_ans

    current_all_row_ans = []
    current_all_col_ans = []

    ans_block_bg_color = "#8CFA6A"
    correct_ans_bg_color = "#013ADF"
    correct_ans_fg_color = "white"

    if first_call is True:  # First time calling the function, create all answer blocks for display.
        # Display Row Answers.
        for row in range(num_of_row.get()):
            row_answer_block = tkinter.Label(game_frame, text=row_ans[row], relief="raised")
            row_answer_block2 = tkinter.Label(game_frame, text=row_ans[row], relief="raised")
            row_answer_block.configure(width=6, height=2, bg=ans_block_bg_color)
            row_answer_block2.configure(width=6, height=2, bg=ans_block_bg_color)

            row_sum = numpy.sum(game_grid[row])
            current_all_row_ans.append(row_sum)

            if row_sum == row_ans[row]:  # Current row answer is achieved.
                row_answer_block.configure(bg=correct_ans_bg_color, fg=correct_ans_fg_color)
                row_answer_block2.configure(bg=correct_ans_bg_color, fg=correct_ans_fg_color)
                row_ans_index_list.append(row)  # Store into list.

            row_answer_block.grid(row=1 + row, column=0, sticky="news", padx=2)
            row_answer_block2.grid(row=1 + row, column=num_of_col.get() + 1, sticky="news", padx=2)

        # Display Column Answers.
        for col in range(num_of_col.get()):
            col_answer_block = tkinter.Label(game_frame, text=col_ans[col], relief="raised")
            col_answer_block2 = tkinter.Label(game_frame, text=col_ans[col], relief="raised")
            col_answer_block.configure(width=6, height=2, bg=ans_block_bg_color)
            col_answer_block2.configure(width=6, height=2, bg=ans_block_bg_color)

            col_sum = 0
            for row in range(num_of_row.get()):
                col_sum += game_grid[row, col]
            current_all_col_ans.append(col_sum)

            if col_sum == col_ans[col]:  # Current column answer is achieved.
                col_answer_block.configure(bg=correct_ans_bg_color, fg=correct_ans_fg_color)
                col_answer_block2.configure(bg=correct_ans_bg_color, fg=correct_ans_fg_color)
                col_ans_index_list.append(col)  # Store into list.

            col_answer_block.grid(row=0, column=1 + col, sticky="news", pady=2)
            col_answer_block2.grid(row=num_of_row.get() + 1, column=1 + col, sticky="news", pady=2)
    else:  # Not first call, don't need to create every answer block again.
        # Check and Display changes in Row Answers.
        for row in range(num_of_row.get()):
            row_sum = numpy.sum(game_grid[row])
            current_all_row_ans.append(row_sum)

            if row_sum == row_ans[row]:  # Current row answer is achieved.
                if row not in row_ans_index_list:  # Current row answer not stored yet.
                    row_answer_block = tkinter.Label(game_frame, text=row_ans[row], relief="raised")
                    row_answer_block2 = tkinter.Label(game_frame, text=row_ans[row], relief="raised")

                    row_answer_block.configure(width=6, height=2, bg=correct_ans_bg_color, fg=correct_ans_fg_color)
                    row_answer_block2.configure(width=6, height=2, bg=correct_ans_bg_color, fg=correct_ans_fg_color)

                    row_answer_block.grid(row=1 + row, column=0, sticky="news", padx=2)
                    row_answer_block2.grid(row=1 + row, column=num_of_col.get() + 1, sticky="news", padx=2)

                    row_ans_index_list.append(row)  # Store into list.
            else:  # Current row answer is not achieved.
                if row in row_ans_index_list:  # Current row answer is stored and needs to be removed.
                    row_answer_block = tkinter.Label(game_frame, text=row_ans[row], relief="raised")
                    row_answer_block2 = tkinter.Label(game_frame, text=row_ans[row], relief="raised")

                    row_answer_block.configure(width=6, height=2, bg=ans_block_bg_color)
                    row_answer_block2.configure(width=6, height=2, bg=ans_block_bg_color)

                    row_answer_block.grid(row=1 + row, column=0, sticky="news", padx=2)
                    row_answer_block2.grid(row=1 + row, column=num_of_col.get() + 1, sticky="news", padx=2)

                    del row_ans_index_list[row_ans_index_list.index(row)]  # Remove from list.

        # Check and Display changes in Column Answers.
        for col in range(num_of_col.get()):
            col_sum = 0
            for row in range(num_of_row.get()):
                col_sum += game_grid[row, col]
            current_all_col_ans.append(col_sum)

            if col_sum == col_ans[col]:  # Current column answer is achieved.
                if col not in col_ans_index_list:  # Current column answer not stored yet.
                    col_answer_block = tkinter.Label(game_frame, text=col_ans[col], relief="raised")
                    col_answer_block2 = tkinter.Label(game_frame, text=col_ans[col], relief="raised")

                    col_answer_block.configure(width=6, height=2, bg=correct_ans_bg_color, fg=correct_ans_fg_color)
                    col_answer_block2.configure(width=6, height=2, bg=correct_ans_bg_color, fg=correct_ans_fg_color)

                    col_answer_block.grid(row=0, column=1 + col, sticky="news", pady=2)
                    col_answer_block2.grid(row=num_of_row.get() + 1, column=1 + col, sticky="news", pady=2)

                    col_ans_index_list.append(col)  # Store into list.
            else:  # Current column answer is not achieved.
                if col in col_ans_index_list:  # Current column answer is stored and needs to be removed.
                    col_answer_block = tkinter.Label(game_frame, text=col_ans[col], relief="raised")
                    col_answer_block2 = tkinter.Label(game_frame, text=col_ans[col], relief="raised")

                    col_answer_block.configure(width=6, height=2, bg=ans_block_bg_color)
                    col_answer_block2.configure(width=6, height=2, bg=ans_block_bg_color)

                    col_answer_block.grid(row=0, column=1 + col, sticky="news", pady=2)
                    col_answer_block2.grid(row=num_of_row.get() + 1, column=1 + col, sticky="news", pady=2)

                    del col_ans_index_list[col_ans_index_list.index(col)]  # Remove from list.

    check_win_game(first_call)
    return


row_ans_info1 = tkinter.Label(info_frame, text="\n- Current Sum Of Each Row [Top - Bottom]:", bg=common_frame_color)
row_ans_info2 = tkinter.Label(info_frame, text=f"{current_all_row_ans}", bg=common_frame_color)

col_ans_info1 = tkinter.Label(info_frame, text="\n- Current Sum Of Each Column [Left - Right]:", bg=common_frame_color)
col_ans_info2 = tkinter.Label(info_frame, text=f"{current_all_col_ans}", bg=common_frame_color)

win_game_text1 = "\nCongratulations!!! You've successfully solved the puzzle!"
win_game_text2 = "You can press the Reset Game button to restart the program or close the window to"
win_game_text3 = "terminate the program."
win_game_info1 = tkinter.Label(info_frame, text=win_game_text1, bg=common_frame_color)
win_game_info2 = tkinter.Label(info_frame, text=win_game_text2, bg=common_frame_color)
win_game_info3 = tkinter.Label(info_frame, text=win_game_text3, bg=common_frame_color)

win_game = False


def check_win_game(first_call):  # Check if the player has solved the puzzle or not and update info frame.
    global row_ans_info1
    global row_ans_info2
    global col_ans_info1
    global col_ans_info2

    global win_game_info1
    global win_game_info2
    global win_game_info3
    global win_game

    if changing_position is True:  # Haven't change positions, no need to check.
        return

    if len(row_ans_index_list) == num_of_row.get() and len(col_ans_index_list) == num_of_col.get():  # Win game.
        # Remove certain info from the frame and display winning message.
        row_ans_info1.destroy()
        row_ans_info2.destroy()

        col_ans_info1.destroy()
        col_ans_info2.destroy()

        win_game_info1.grid(row=3, column=0, sticky="w")
        win_game_info2.grid(row=4, column=0, sticky="w")
        win_game_info3.grid(row=5, column=0, sticky="w")

        win_game = True  # True until the whole script is re-executed again.
        return

    if first_call is True:  # First call, display all info.
        row_ans_info2.configure(text=f"{current_all_row_ans}")
        col_ans_info2.configure(text=f"{current_all_col_ans}")

        row_ans_info1.grid(row=3, column=0, sticky="w")
        row_ans_info2.grid(row=4, column=0, sticky="w")

        col_ans_info1.grid(row=5, column=0, sticky="w")
        col_ans_info2.grid(row=6, column=0, sticky="w")
    else:  # Upgrade certain info only.
        row_ans_info2.configure(text=f"{current_all_row_ans}")
        col_ans_info2.configure(text=f"{current_all_col_ans}")

        row_ans_info2.grid(row=4, column=0, sticky="w")
        col_ans_info2.grid(row=6, column=0, sticky="w")
    return


option_position1 = None  # After the first press on an option, its position [row, col] is stored here.
option_position2 = None  # After the second press on another option, its position [row, col] is stored here.
changing_position = False  # Default = False. True if it's in the process of changing positions of options.


def update_game_grid(first_call):  # Display all options of the puzzle.
    global option_position1
    global option_position2

    def change_position(row, col):  # Exchange positions of 2 options.
        global option_position1
        global option_position2
        global changing_position
        global game_grid

        if win_game is True:  # Already solved the puzzle, make all buttons useless now.
            return

        if option_position1 is None:  # First call, store position of the option only.
            option_position1 = (row, col)
            changing_position = True  # True if still in the process of changing positions.

            thread1 = threading.Thread(target=update_answer_frame, args=(False,))
            thread2 = threading.Thread(target=update_game_grid, args=(False,))
            thread1.start()
            thread2.start()
            return

        # Second call, exchange positions.
        option_position2 = (row, col)  # Store position of the second option.
        backup_grid = game_grid.copy()  # As reference for changing the real game grid.

        game_grid[option_position1[0], option_position1[-1]] = backup_grid[option_position2[0], option_position2[-1]]
        game_grid[option_position2[0], option_position2[-1]] = backup_grid[option_position1[0], option_position1[-1]]

        changing_position = False  # False if already finished changing positions.

        thread1 = threading.Thread(target=update_answer_frame, args=(False,))
        thread2 = threading.Thread(target=update_game_grid, args=(False,))
        thread1.start()
        thread2.start()
        return

    option_active_bg = "#03F9E4"

    # Main part of displaying the options.
    for option_row in range(num_of_row.get()):
        for option_col in range(num_of_col.get()):
            if first_call is True:  # First call, create all option buttons with their respective function.
                option_button = tkinter.Button(game_frame, text=f"{game_grid[option_row, option_col]}",
                                               command=lambda row=option_row, col=option_col: change_position(row, col))

                option_button.configure(width=6, height=2, activebackground=option_active_bg, bg=common_button_color)

                option_button.grid(row=option_row + 1, column=option_col + 1)

            # The position of first option is stored already and reached now.
            if option_position1 == (option_row, option_col):
                option_button = tkinter.Button(game_frame, text=f"{game_grid[option_row, option_col]}",
                                               command=lambda row=option_row, col=option_col: change_position(row, col))

                option_button.configure(width=6, height=2)

                if changing_position is True:  # Haven't got the position of second option.
                    option_button.configure(bg=option_active_bg, activebackground=common_button_color)
                else:  # Changed positions. Can remove the stored position of first option now.
                    option_position1 = None
                    option_button.configure(activebackground=option_active_bg, bg=common_button_color)

                option_button.grid(row=option_row + 1, column=option_col + 1)

            # The position of second option is stored already and reached now.
            if option_position2 == (option_row, option_col):
                option_button = tkinter.Button(game_frame, text=f"{game_grid[option_row, option_col]}",
                                               command=lambda row=option_row, col=option_col: change_position(row, col))

                option_button.configure(width=6, height=2, activebackground=option_active_bg, bg=common_button_color)

                option_position2 = None  # Changed positions. Can remove the stored position of second option now.

                option_button.grid(row=option_row + 1, column=option_col + 1)
    return


get_game_settings()

game_windows.update_idletasks()

win_width = game_windows.winfo_reqwidth()
win_height = game_windows.winfo_reqheight()
screen_width = game_windows.winfo_screenwidth()
screen_height = game_windows.winfo_screenheight()

x_coord = int(screen_width / 2 - win_width / 2)
y_coord = int(screen_height / 7 - win_height / 2)

game_windows.geometry(f"+{x_coord}+{y_coord}")

game_windows.resizable(0, 0)
game_windows.mainloop()

# This program is COMPLETED. Date : 25/7/2020 4:23 PM
