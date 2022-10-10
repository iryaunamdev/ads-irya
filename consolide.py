"""
Consolidate all searches by author/orcid into one new JSON file    
"""

import sys
import os
import json
from getads import fuzzy
from fuzzywuzzy import process
import datetime

try:
    WORKDIR = sys.argv[1]
except IndexError:
    sys.exit(f"Usage: {sys.argv[0]} WORKDIR")
    
REFERENCE_FILE = "data/irya.list.json"

with open(REFERENCE_FILE) as json_file:
    author_list = json.load(json_file)
    
#Read everyfile in WORKDIR/author
papers = {}
for id, author in author_list.items():
    print(author['author'])
    papers_author = {}
    #Read everyfile in WORKDIR/author
    for filename in os.listdir(f"{WORKDIR}/author"):
        if fuzzy(author['author']) in filename:
            with open(filename) as json_author_file:
                papers_info = json.load(json_author_file)
            
            for bibcode, paper in papers_info:
                papers_author[bibcode] = paper
                papers_author['match_author'] = process.extractOne(author['author'], paper['author'])
                papers_author['match_orcid'] = process.extractOne(author['orcid'], paper['orcid_user'])
        
    #Read everyfile in WORKDIR/author
    for filename in os.listdir(f"{WORKDIR}/orcid"):
        if fuzzy(author['author']) in filename:
            with open(filename) as json_author_file:
                papers_info = json.load(json_author_file)
            
            for bibcode, paper in papers_info:
                if bibcode not in papers_author.keys():
                    papers_author[bibcode] = paper
                    papers_author['match_author'] = process.extractOne(author['author'], paper['author'])
                    papers_author['match_orcid'] = process.extractOne(author['orcid'], paper['orcid_user'])
    
    date = datetime.now().strftime('%Y%m%d')
    with open(f"consolidated/{date}_{id}_{fuzzy(author['author'])}", '+w', encoding='utf-8') as outfile:
        json.dump(papers_author, outfile, ensure_ascii=False)