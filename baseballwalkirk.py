import sys
import pybaseball
import pandas as pd
import pprint
import numpy as np
import tkinter as tk
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt


###### CONSTANTS #####
MATRIX_ROWS = 12
MATRIX_COLS = 19

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

def display_matrix(matrix, player_name):
    num_rows, num_cols = len(matrix), len(matrix[0])
    cell_width = 40

    # Define row and column labels
    row_labels = ['0-0', '0-1', '1-0', '0-2', '1-1', '2-0', '1-2', '2-1', '3-0', '2-2', '3-1', '3-2']
    col_labels = row_labels + ['1B', '2B', '3B', 'HR', 'BIP', 'BB', 'K']

    # Create the Qt application
    app = QApplication(sys.argv)

    # Create the main window
    window = QMainWindow()
    window.setWindowTitle("Matrix Display for " + player_name)

    dark_gray = QColor(40, 40, 40)
    window.setStyleSheet(f"background-color: {dark_gray.name()};")

    # Create a central widget to hold the layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)

    # Create a vertical layout for the central widget
    layout = QVBoxLayout()
    central_widget.setLayout(layout)

    # Create the table to display the matrix
    for i in range(num_rows + 1):
        row_layout = QHBoxLayout()
        for j in range(num_cols + 1):
            if i == 0 and j == 0:
                # Top-left cell: empty label
                label = QLabel()
            elif i == 0:
                # Column labels
                label = QLabel(col_labels[j - 1])
            elif j == 0:
                # Row labels
                label = QLabel(row_labels[i - 1])
            else:
                # Matrix values
                val = matrix[i - 1][j - 1]
                g = int(val * 400)  # Adjust the range of green component for a more drastic change
                color = QColor(0, g, 0)  # Adjusted green color
                text_color = QColor(255, 255, 255) if val != 1 else QColor(0, 0, 0)  # White text for non-zero values, black for zeros
                label = QLabel(f"{val:.3f}")

                # Set the background and text color
                label.setAutoFillBackground(True)
                label.setStyleSheet(f"background-color: {color.name()}; color: {text_color.name()};")

            label.setAlignment(Qt.AlignCenter)  # Center the label text
            label.setFixedSize(cell_width, cell_width)
            row_layout.addWidget(label)

        layout.addLayout(row_layout)

    # Show the window
    window.show()

    # Start the Qt event loop
    sys.exit(app.exec_())


def construct_transition_matrix(player_name):

    player_stats = lookup_player_statcast(player_name)
    selected_columns = ['game_date', 'balls', 'strikes','at_bat_number', "pitch_number",'events','description', 'game_type']
    parsed_data = player_stats[selected_columns]
    #print(parsed_data)

    matrix = np.ones((MATRIX_ROWS, MATRIX_COLS))

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
            elif i == 1:
                if j == 0:
                    matrix[2][4] = (strike + foul) / row_count
                    matrix[2][5] = ball / row_count
                    matrix[2][12] = single / row_count
                    matrix[2][13] = double/ row_count
                    matrix[2][14] = triple/ row_count
                    matrix[2][15] = homer/ row_count
                    matrix[2][16] = BIP / row_count
                elif j == 1:
                    matrix[4][6] = (strike + foul) / row_count
                    matrix[4][7] = ball / row_count
                    matrix[4][12] = single / row_count
                    matrix[4][13] = double/ row_count
                    matrix[4][14] = triple/ row_count
                    matrix[4][15] = homer/ row_count
                    matrix[4][16] = BIP / row_count
                elif j == 2:
                    matrix[6][18] = strike / row_count
                    matrix[6][6] = foul / row_count
                    matrix[6][9] = ball / row_count
                    matrix[6][12] = single / row_count
                    matrix[6][13] = double/ row_count
                    matrix[6][14] = triple/ row_count
                    matrix[6][15] = homer/ row_count
                    matrix[6][16] = BIP / row_count
            elif i == 2:
                if j == 0:
                    matrix[5][7] = (strike + foul) / row_count
                    matrix[5][8] = ball / row_count
                    matrix[5][12] = single / row_count
                    matrix[5][13] = double/ row_count
                    matrix[5][14] = triple/ row_count
                    matrix[5][15] = homer/ row_count
                    matrix[5][16] = BIP / row_count
                elif j == 1:
                    matrix[7][9] = (strike + foul) / row_count
                    matrix[7][10] = ball / row_count
                    matrix[7][12] = single / row_count
                    matrix[7][13] = double/ row_count
                    matrix[7][14] = triple/ row_count
                    matrix[7][15] = homer/ row_count
                    matrix[7][16] = BIP / row_count
                elif j == 2:
                    matrix[9][18] = strike / row_count
                    matrix[9][9] = foul / row_count
                    matrix[9][11] = ball / row_count
                    matrix[9][12] = single / row_count
                    matrix[9][13] = double/ row_count
                    matrix[9][14] = triple/ row_count
                    matrix[9][15] = homer/ row_count
                    matrix[9][16] = BIP / row_count




        


           

    display_matrix(matrix, player_name)



if __name__ == "__main__":
    #player_name = 'joey wiemer'
    player_name = 'shohei ohtani'
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