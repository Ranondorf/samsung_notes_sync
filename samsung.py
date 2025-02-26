#!/usr/bin/env python3
"""Put Samsung notes workout plans into a csv.
"""

import os
import sys
import shutil
import csv


def rename_files(root_path: str, output_folder: str) -> None:
    """Takes samsung notes text files and renames them to YYMMDD_Day.txt or YYMMDD_Day_NNkg.txt.
    
    Args:
        root_path: Source dir that contains the text files
        output_folder: Destination dir for the renamed versions of the text file
    """
    old_style = False
    for file in os.listdir(root_path):
        if file.endswith(".txt"):
            split_space = file.split(" ")
            split_underscore = split_space[2].split("_")
            informal_date = split_space[0] # This is the user written date provided as DMYY
            try:
                ref_date = split_underscore[1] # This is the last modified date from samsung notes
            except IndexError as e:
                # This must be an old format type file
                split_underscore = split_space[1].split("_")
                ref_date = split_underscore[1]
                old_style = True
            except Exception as e:
                print(e)
                print('split_space: ', split_space)
                print('split_underscore: ', split_underscore)
                sys.exit(1)

            day = split_space[1][0:3]
            weight = split_underscore[0].rstrip("kgKG") if not old_style else '00'

            if len(informal_date) == 4:
                date = f'{informal_date[2:]}0{informal_date[1]}0{informal_date[0]}'
            elif len(informal_date) == 5:
                if int(informal_date[0:2]) > 31:
                    date = f'{informal_date[3:]}{informal_date[1:3]}0{informal_date[0]}'
                elif int(informal_date[1:3]) > 12 or informal_date[1] == '0':
                    date = f'{informal_date[3:]}0{informal_date[2]}{informal_date[0:2]}'
                else:
                    print("Else catch", informal_date, ref_date)
            elif len(informal_date)  == 6:
                date = f'{informal_date[4:]}{informal_date[2:4]}{informal_date[0:2]}'
            else:
                print("Something has gone wrong")
            
            # This is a sanity check provided so if there are big discrepancies, numbers over abs(100) should be investigated
            if abs(int(date) - int(ref_date)) > 100:
                print('\nThe following file has a difference between modified and reported date, please inspect manually:')
                print(f'{date}_{day}_{weight} - {ref_date} - diff: {int(date) - int(ref_date)}')
            
            # This copies the modified txt files into the destination
            shutil.copy2(os.path.join(root_path, file),os.path.join(output_folder, f'{date}_{day}_{weight}kg.txt'))
            


def create_output_csv(output_folder: str, output_file: str):
    """Takes a bunch of files and parses them into a CSV"""
    output_csv = os.path.join(output_folder, output_file)
    entries = []
    for filename in sorted([f for f in os.listdir(output_folder) if f.endswith(".txt")]):
        with open(os.path.join(output_folder, filename)) as file_handle:
            lines = [f'{filename[4:6]}/{filename[2:4]}/20{filename[0:2]}', filename[7:10]]
            if len(filename.rstrip(".tx")) > 10:
                lines += [filename[11:15]]
            lines += [line.rstrip() for line in file_handle.readlines()]
            entries.append(lines)

    max_length = max(len(lines) for lines in entries)

    for i in range(len(entries)):
        if len(entries[i]) < max_length:
            entries[i].extend([''] * (max_length - len(entries[i])))

    with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        for row in zip(*entries):
            writer.writerow(row)


def main():
    root_path = sys.argv[1] # Path to the folder containing the samsung notes generated text files
    output_folder = sys.argv[2] # Destination path to where all output files including the CSV goes

    print("\n\nEntering Phase 1\n\n")
    rename_files(root_path, output_folder)    
    print("\n\nEntering Phase 2\n\n")
    create_output_csv(output_folder, 'output.csv')
    print("Finished")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        sys.exit(1)