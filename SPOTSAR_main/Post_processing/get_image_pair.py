import os
import numpy as np
import re

def get_image_pairs(folder_path, regex_str, length):
    # Get a list of all files in the folder
    files = os.listdir(folder_path)
    print("number of files:", np.size(files))

    # Define the regular expression pattern
    pattern = re.compile(regex_str)

    # Filter and sort files based on the first 11 characters
    sorted_files = sorted(
        [file for file in files if pattern.match(file)], key=lambda x: x[:length]
    )
    print("number of files mathing pattern:", np.size(sorted_files))

    unique_files = []
    for file in sorted_files:
        if file[:length] not in unique_files:
            unique_files.append(file[:length])

    print("number of unique image pairs:", np.size(unique_files))
    return unique_files