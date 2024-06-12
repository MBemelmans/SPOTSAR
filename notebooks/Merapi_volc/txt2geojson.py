# Convert text file to JSON 

import sys
sys.path.append('../../')
sys.path.append('/Applications/anaconda3/envs/PhD_clean/lib/python3.11/site-packages/')

import json
import geojson 
with open('/Users/tz20896/Documents/PhD/projects/SPOTSAR/notebooks/Merapi_volc/towns_indonesia.txt') as json_file:     # name of the text file
    data = json.load(json_file)

# Convert JSON to GeoJson 
from geojson import dump
with open('/Users/tz20896/Documents/PhD/projects/SPOTSAR/notebooks/Merapi_volc/towns_indonesia.geojson', 'w') as f:   # name of the output geojson file
   dump(data, f)