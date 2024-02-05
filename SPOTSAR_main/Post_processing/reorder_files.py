import os
import re
import numpy as np

def reorder_files(dir,pattern,mode=0):
    """
        retrieve txt files and reorder them in ascending or 
        descending order based on window size
        ...
        INPUT:
            dir:        directory where files are located
            pattern:    regex pattern used for file matching
            mode:       0 (default) for ascending, 1 for descending

        output:
            ord_files:  ordered file list
    """

    # Create an empty list to store the matching file names
    matching_files_q = [] 
    win1_size = []
    # Loop through all the files in the directory
    for filename in os.listdir(dir):

        # Check if the file name matches the regular expression
        if re.match(pattern, filename):
            # matching files are always of the format [a-z]yyyymmdd_[a-z]yyyymmdd_disp_win1_win2.txt
            # split parts 3 and 4 link to win1,win2
            win1_size.append(int(filename.split('_')[3]))
            # If it matches, add the file name to the list
            matching_files_q.append(filename)
    
    indices = np.argsort(win1_size)
    return [matching_files_q[i] for i in indices]