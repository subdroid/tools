"""
Copyleft 2024, Sunit Bhattacharya
Institute of Formal and Applied Linguistics,
Charles University in Prague, Czech Republic.


Usage:
    python coltoro.py input.csv -d '\t' -s 10

"""

import csv
import sys
import argparse
import os
import pandas as pd
import numpy as np
import subprocess
import tempfile

def transform_and_display(file_path, delimiter=',', line_spacing=10):
    """
    Transforms the columns of a file into rows and displays them with specified line spacing.

    Args:
    - file_path (str): Path to the file.
    - delimiter (str): The delimiter used in the file. Defaults to ','.
    - line_spacing (int): The number of blank lines between rows. Defaults to 10.

    Returns:
    None
    """
    df = pd.read_csv(file_path, header=None, sep=delimiter, engine='python')
      
    num_rows, num_cols = df.shape
    
    with tempfile.NamedTemporaryFile(mode='w') as tmp_file:
        for i in range(num_rows):
            for j in range(num_cols):
                print(df.iat[i, j].strip(), file=tmp_file)
            if i < num_rows - 1:
                print("\n" * line_spacing, file=tmp_file)  # Line spacing between rows

        # Open the temporary file in vim for editing
        subprocess.run(['vim', tmp_file.name])

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Convert any multi-column file into a multi-row view")
    parser.add_argument("input", help="Input file")
    parser.add_argument("-d", "--delimiter", type=str, default=",", help="Delimiter symbol (default:,)")
    parser.add_argument("-s", "--spacing",   type=int, default=2, help="Spacing between rows (default: 10)")
    args = parser.parse_args()


    file_path = args.input
    delimiter = args.delimiter
    line_spacing = args.spacing

    transform_and_display(file_path, delimiter, line_spacing)
