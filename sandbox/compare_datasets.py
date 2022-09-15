'''
Load and compare two csv files.
This script can be used to verify whether two simulations have produced exactly the same outputs. This can be useful to validate, whether the random seed produced the same outputs.
'''

import pandas
import os

folder1 = '../../data/outputs/output_20220915_10-20-21'
folder2 = '../../data/outputs/output_20220915_10-28-58'

############################### load data #############################
list_of_files = [[], []]
folder_idx = 0
for folder in folder1, folder2:
    for root, dirs, files in os.walk(folder, topdown=False):
        for name in files:
            if name[-4:].__eq__('.csv'):
                list_of_files[folder_idx].append(os.path.join(root, name))

    folder_idx += 1

print("found files: ", list_of_files)
############################ compare data #############################
# connections_df1 = pandas.read_csv(folder1 + '/connections/connections_export.csv')
# connections_df2 = pandas.read_csv(folder2 + '/connections/connections_export.csv')
for i in range(len(list_of_files[0])):
    print("#"*72)
    print("comparing {0} with {1}: ".format(list_of_files[0][i], list_of_files[1][i]))
    if pandas.read_csv(list_of_files[0][i]).compare(pandas.read_csv(list_of_files[1][i])).empty:
        print("both simulations produced the same results!")
    else:
        print(pandas.read_csv(list_of_files[0][i]).compare(pandas.read_csv(list_of_files[1][i])))