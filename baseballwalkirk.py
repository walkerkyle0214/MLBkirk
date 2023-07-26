import sys
import pybaseball
import pandas as pd
import pprint
import numpy as np
import tkinter as tk

def separate_name(player_name):
    # Split the full name into first name and last name
    names = player_name.split()

    if len(names) == 1:
        # Only one name provided (e.g., aaron), consider it as the first name
        first_name = names[0]
        last_name = ""
    else:
        # First name is the first word, last name is the last word
        first_name = names[0]
        last_name = names[-1]

    return names


def get_player_id(player_name):

    name = separate_name(player_name)

    # Use playerid_lookup to retrieve the player ID
    player_id = pybaseball.playerid_lookup(name[-1], name[0])

    if player_id.empty:
        print(f"Player ID not found for: {player_name}")
        sys.exit()

    return player_id['key_mlbam'].values[0]


def lookup_player_statcast(player_name):
    # Get the player ID
    player_id = get_player_id(player_name)

    # Fetch statcast data for the specified player with one ball and one strike
    statcast_data = pybaseball.statcast_batter('2019-01-01','2023-06-21',player_id = player_id)

    # Check if no data found for the player and exit if so
    if statcast_data.empty:
        print(f"No stats found for player: {player_name}")
        sys.exit()

    return statcast_data


def lookup_batting_stats(player_name):
    season = 2023
    pybaseball.cache.enable()

    # Fetch batting stats for the specified season with a minimum qualifying threshold
    batting = pybaseball.batting_stats(season, qual=1)

    # Find the row corresponding to the specified player name
    row_data = batting[batting['Name'] == player_name]

    # Check if no stats found for the player and return None if so
    if row_data.empty:
        print(f"No batting stats found for player: {player_name}")
        return None

    # Create a dictionary to store player batting stats
    stats_dict = {}
    for column_name, value in row_data.iloc[0].iteritems():
        stats_dict[column_name] = value

    return stats_dict


def lookup_pitching_stats(player_name):
    season = 2023
    pybaseball.cache.enable()

    # Fetch pitching stats for the specified season
    pitching = pybaseball.pitching_stats(season)

    # Find the row corresponding to the specified player name
    row_data = pitching[pitching['Name'] == player_name]

    # Check if no stats found for the player and return None if so
    if row_data.empty:
        print(f"No pitching stats found for player: {player_name}")
        return None

    # Create a dictionary to store player pitching stats
    stats_dict = {}
    for column_name, value in row_data.iloc[0].iteritems():
        stats_dict[column_name] = value
    return stats_dict


def display_matrix(matrix):
    num_rows, num_cols = matrix.shape
    cell_width = 6

    # Create a Tkinter window
    window = tk.Tk()
    window.title("Matrix Display")

    # Create a table to display the matrix
    table = tk.Frame(window)
    table.pack()

    # Create row and column labels
    row_labels = ['0-0','0-1','1-0','0-2','1-1','2-0','1-2','2-1','3-0','2-2','3-1','3-2']
    col_labels = row_labels + ['1B','2B','3B','HR','BIP','BB','K']

    # Add column labels
    for i, label in enumerate(col_labels):
        col_label = tk.Label(table, text=label, width=cell_width, relief=tk.RIDGE)
        col_label.grid(row=0, column=i + 1)  # Place labels in the first row, starting from column 1

    # Populate the table with matrix values and labels
    for i, row in enumerate(matrix):
        # Add row labels
        row_label = tk.Label(table, text=row_labels[i], width=cell_width, relief=tk.RIDGE)
        row_label.grid(row=i + 1, column=0)  # Place labels in the corresponding row, in the first column

        # Add matrix values
        for j, val in enumerate(row):
            if val != 0:
                # Calculate the color based on the value (example gradient)
                g = int(val * 400) # Adjust the range of green component for lighter shade
                color = f'#00{g:02x}00'  # RGB color format with adjusted green component
                text_color = '#FFFFFF' 

                # Create a label with the corresponding color
                label = tk.Label(table, text=f"{val:.3f}", width=cell_width, relief=tk.RIDGE, bg=color, fg =text_color)
            else:
                # Empty label if the value is 0
                label = tk.Label(table, text="", width=cell_width, relief=tk.RIDGE)
            label.grid(row=i + 1, column=j + 1)  # Place matrix values in the corresponding row and column
    # Start the Tkinter event loop
    window.mainloop()


def construct_transition_matrix(player_name):

    player_stats = lookup_player_statcast(player_name)
    selected_columns = ['game_date', 'balls', 'strikes','at_bat_number', "pitch_number",'events','description', 'game_type']
    parsed_data = player_stats[selected_columns]
    #print(parsed_data)

    matrix = np.zeros((12, 19))

    for i in range(4):
        for j in range(3):
            filtered_data = parsed_data.loc[(parsed_data['balls'] == i) & (parsed_data['strikes'] == j) & (parsed_data["game_type"] == 'R')]

            row_count = len(filtered_data)
            counts = filtered_data['description'].value_counts()

            ball = counts.get('ball', 0) + counts.get('blocked_ball', 0)
            strike = counts.get('called_strike', 0) + counts.get('swinging_strike', 0) + counts.get('swinging_strike_blocked', 0)
            foul = counts.get('foul', 0) + counts.get('foul_tip', 0)

            counts = filtered_data['events'].value_counts()

            single = counts.get('single', 0)
            double = counts.get('double', 0)
            triple = counts.get('triple', 0)
            homer = counts.get('home_run', 0)
            BIP = row_count - single - double - triple - homer - ball - strike - foul

            print("Ball:", ball)
            print("Strike:", strike)
            print("Foul:", foul)
            print("BIP:", BIP)
            print("Single:", single)
            print("Double:", double)
            print("Triple:", triple)
            print("Home Run:", homer)
            print("Total:", row_count)

            if i == 0:
                if j == 0:
                    matrix[0][1] = (strike + foul) / row_count
                    matrix[0][2] = ball / row_count
                    matrix[0][12] = single / row_count
                    matrix[0][13] = double/ row_count
                    matrix[0][14] = triple/ row_count
                    matrix[0][15] = homer/ row_count
                    matrix[0][16] = BIP / row_count
                elif j == 1:
                    matrix[1][3] = (strike + foul) / row_count
                    matrix[1][4] = ball / row_count
                    matrix[1][12] = single / row_count
                    matrix[1][13] = double/ row_count
                    matrix[1][14] = triple/ row_count
                    matrix[1][15] = homer/ row_count
                    matrix[1][16] = BIP / row_count
                elif j == 2:
                    matrix[3][18] = strike / row_count
                    matrix[3][3] = foul / row_count
                    matrix[3][6] = ball / row_count
                    matrix[3][12] = single / row_count
                    matrix[3][13] = double/ row_count
                    matrix[3][14] = triple/ row_count
                    matrix[3][15] = homer/ row_count
                    matrix[3][16] = BIP / row_count
      



           

    display_matrix(matrix)



if __name__ == "__main__":
    #player_name = 'joey wiemer'
    player_name = 'luis arraez'
    #player_name = 'giancarlo stanton'

    """# Lookup batting stats for the specified player
    batting_stats = lookup_batting_stats(player_name)
    if batting_stats:
        pprint.pprint(batting_stats)

    # Lookup pitching stats for the specified player
    pitching_stats = lookup_pitching_stats(player_name)
    if pitching_stats:
        pprint.pprint(pitching_stats)

    player_stats = lookup_player_statcast(player_name)
    print(player_stats)"""

    pd.set_option('display.max_rows', None)

    construct_transition_matrix(player_name)

    sys.exit(0)
