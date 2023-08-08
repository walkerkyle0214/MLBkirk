import baseballwalkirk as bb
import os
import sys
import pybaseball
import pandas as pd
import pprint
import numpy as np
import random as rand
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt


def at_bat(hitter_matrix, pitcher_matrix):

    current_state = 0

    #12 or greater refers to the first state where an atbat ends in an event
    while current_state < 12:
        random_float = rand.random()
        print("*****finding next state*****")
        total = 0
        for i in range(len(hitter_matrix[current_state])):
            if not hitter_matrix[current_state][i] == 1:
                if random_float > total and random_float < total+hitter_matrix[current_state][i]:
                    current_state = i
                    print(current_state)
                    break
                else:
                    total += hitter_matrix[current_state][i]








def write_matrix_to_file(matrix, foldername, filename):
    try:
        # Create the folder if it doesn't exist
        if not os.path.exists(foldername):
            os.makedirs(foldername)

        filepath = os.path.join(foldername, filename)

        with open(filepath, 'w') as file:
            for row in matrix:
                row_str = ' '.join(str(element) for element in row)
                file.write(row_str + '\n')
        print(f"Matrix successfully written to {filepath}")
    except Exception as e:
        print(f"Error writing to {filepath}: {e}")

def read_matrix_from_file(filepath):
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()
            matrix = [list(map(float, line.strip().split())) for line in lines]
        return matrix
    except Exception as e:
        print(f"Error reading from {filepath}: {e}")
        return None







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

    filepath = os.path.join('hitter_stats', player_name)
    matrix = read_matrix_from_file(filepath)
    at_bat(matrix, matrix)
    bb.display_matrix(matrix, player_name)


    sys.exit(0)








