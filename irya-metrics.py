import json
import sys


with open('data/author_01.json') as json_file:
    data = json.load(json_file)
    
for bibcode, paper  in data.items():
    print(paper)