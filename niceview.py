"""
Copyleft 2024, Sunit Bhattacharya
Institute of Formal and Applied Linguistics,
Charles University in Prague, Czech Republic.


This script reads a CSV file and outputs a formatted version of the CSV file with the following features:
- Each column is left-aligned
- The width of each column is the maximum width of the column header and the data
- The columns are separated by a specified number of spaces
- The data is rounded to a specified number of decimal places
- The rows are sorted based on a specified column index

Usage:  
    python niceview.py input.csv -s 10 -d 2 -c 1

Arguments:
    input.csv: Input CSV file
    -s/--column-spacing: Spacing between columns (default: 10)
    -d/--decimal-places: Number of decimal places to round to (default: 2)
    -c/--sort-column: Sort rows based on the specified column index (starting from 1)

Output:
    A formatted version of the input CSV file


"""

import csv
import argparse
import os
import pandas as pd
import numpy as np

def beautify_csv(inp, out, column_spacing, decimal_places, sort_column):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(inp, dtype=str)
    
    # Attempt to convert all columns to float where possible
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
            df[col] = df[col].round(decimal_places)
        except ValueError:
            pass
    
    # Sort the DataFrame based on the specified column

    try:
        sort_column = int(sort_column)
        if sort_column > 0 and sort_column <= len(df.columns):
            # print(df.columns[sort_column - 1])
            df = df.sort_values(by=df.columns[sort_column - 1])
        else:
            print("Error: Invalid sort column index.")
            exit(1)
    except ValueError:
        print("Error: Invalid sort column index.")
        exit(1)

    # Convert the DataFrame to a list of strings, where each row is a string
    rows = []
    
    # Calculate the maximum width of each column
    col_widths = [max(max(len(str(item)), len(col)) for item in df[col]) for col in df.columns]
    
    # Create a header with spacing
    header = []
    for i, col in enumerate(df.columns):
        header.append(col.ljust(col_widths[i] + column_spacing))
    rows.append(''.join(header))

    
    # Create each row with spacing
    for index, row in df.iterrows():
        row_data = []
        for i, col in enumerate(df.columns):
            row_data.append(str(row[col]).ljust(col_widths[i] + column_spacing))
        rows.append(''.join(row_data))

    with open(out, 'w', newline='') as tsv_file:
            tsv_file.write('\n'.join(rows))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nice view of any CSV file")
    parser.add_argument("input", help="Input file")
    parser.add_argument("-s", "--column-spacing", type=int, default=10, help="Spacing between columns (default: 10)")
    parser.add_argument("-d", "--decimal-places", type=int, default=2, help="Number of decimal places to round to (default: 2)")
    parser.add_argument("-c", "--sort-column", type=int, default=0, help="Sort rows based on the specified column index (starting from 1)")
    args = parser.parse_args()

    # Check if input file exists
    if not os.path.exists(args.input):
        print("Error: Input file '{}' not found.".format(args.input))
        exit(1)

    output_file = "niceview_"+args.input.split(".")[0]
    beautify_csv(args.input, output_file,  args.column_spacing, args.decimal_places, args.sort_column)


    
