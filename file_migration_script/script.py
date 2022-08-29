# %%
import os
import re
import pandas as pd
from urllib.parse import quote

files = [(file, os.path.join(root, file)) for root, subdirs, files in os.walk('files') for file in files]


# %%


valid_file_regex = re.compile(r'^[a-zA-Z0-9_.-]*$')

invalid_files = list(filter(lambda x: re.match(valid_file_regex, x[0]) == None, files))


# %%
# loading csv files in memory

csvs = {}

CSV_FILE_PATH = 'csv'

for f in os.listdir(CSV_FILE_PATH):
    csv = pd.read_csv(os.path.join(CSV_FILE_PATH, f), dtype=str)
    csvs[f] = csv


# %%


# Building a table to store invalid file names and it's reference in csv

# The key of the dict is "File path" 
# The value is a tuple of the form: (Encoded file path, filename, List of references)
# List of references is list containing tuple of the form: (csv file name, column number, row number)

invalid_file_table = {}

# iterating over each invalid file
for fileName, filePath in invalid_files:
    encodedPath = quote(filePath)
    listReferences = []
    for csv_file_name in csvs:
        csv_dataframe = csvs[csv_file_name]
        num_cols = len(csv_dataframe.columns)

        for col_i in range(num_cols):
            col_series = csv_dataframe.iloc[:,col_i].dropna()
            contains_series = col_series.str.contains(encodedPath)

            contains_indices = list(contains_series[contains_series].index)

            for row_j in contains_indices:
                listReferences.append((csv_file_name, col_i, row_j))

    invalid_file_table[filePath] = (encodedPath, fileName, listReferences)


# %%

existing_files_set = set(map(lambda x: x[1], files))
new_files_set = set()

rename_table = {}

valid_char = re.compile(r'[a-zA-Z0-9_.-]')

path_gen = lambda op, nn: "/".join( op.split('/')[:-1] + [ nn ])

for path in invalid_file_table:

    name = invalid_file_table[path][1]
    new_name = "".join(map( lambda x : '_'  if valid_char.match(x) == None else x, name ))

    new_path = path_gen(path, new_name)

    counter = 1
    append_counter = False

    while new_path in existing_files_set or new_path in new_files_set:
        name_splits = new_name.split('.')
        idx = -2 if len(name_splits) > 1 else -1
        frag = name_splits[idx][:-4] if append_counter else name_splits[idx]
        frag += f'_{counter:03d}'
        name_splits[idx] = frag
        new_name = ".".join(name_splits)
        new_path = path_gen(new_path, new_name)
        append_counter = True
        counter += 1

    new_files_set.add(new_path)    

    rename_table[path] = (new_path, new_name)


# %%


# Checking collision after renaming
path_set = {}

for old_path in rename_table:
    new_path, new_name = rename_table[old_path]
    
    if new_path in existing_files_set:
        if new_path in path_set:
            path_set[new_path].add(new_path)
        else:
            path_set[new_path] = set([new_path])

    if new_path in path_set:
        path_set[new_path].add(old_path)
    else:
        path_set[new_path] = set([old_path])

collision_table = {k: path_set[k] for k in path_set if len(path_set[k]) > 1 }

logFile = open("operations.log", 'at')

for old_path in invalid_file_table:
    new_path, new_name = rename_table[old_path]

    ret_mv = os.system(f'git mv "{old_path}" "{new_path}"')

    if ret_mv != 0:
        print(f"Error with renaming file: {old_path}")
        break
    
    # Add to log
    logFile.write(f'{old_path}::renamed to::{new_path}\n')

    encoded_new_path = quote(new_path)

    for csv_file_name, col, row in invalid_file_table[old_path][2]:
        csv_file = csvs[csv_file_name]

        orig_cont = csv_file.iloc[row, col]
        replaced_cont = orig_cont.replace(invalid_file_table[old_path][0], encoded_new_path)

        csv_file.iloc[row, col] = replaced_cont

        logFile.write(f"{csv_file_name}:{row},{col}::\n")
        logFile.write(f"{orig_cont}\n")
        logFile.write(f"{replaced_cont}\n\n")

logFile.close()




