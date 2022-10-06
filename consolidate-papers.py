import json
import sys
from datetime import datetime

"""
Script for consolidate orcid_papers with author papers search results
into a new .json file
"""

def consolidatePapers(papersA, papersO):
    papers = {}
    for key, paper in papersO.items():
        papers[key] = paper
    
    for key, paper in papersA.items():
        if key not in papers:
            papers[key] = paper
    
    return papers
        
IRYA_LIST = sys.argv[1]
author_list_file = open(IRYA_LIST, 'r')
author_list = author_list_file.read().split('\n')

papersIRyA = {}
for author in author_list:
    author = author.split('|')
    papersA = {}
    papersO = {}
    papersAll = {}
    
    with open('data/author_'+author[0]+'.json') as json_file:
        papersA = json.load(json_file)
    if author[1]:
        with open('data/orcid_'+author[0]+'.json') as json_file:
            papersO = json.load(json_file)
        papersAll = consolidatePapers(papersA, papersO)
    else:
        papersAll = papersA 
        
    print(author, "papersByauthor:", len(papersA), 'papersByOrcid', len(papersO), 'consolidatedPapers', len(papersAll))
    
    papersIRyA[author[0]] = papersAll

    with open("data/papers_irya.json", "w", encoding='utf-8') as outfile:
        json.dump(papersIRyA, outfile, ensure_ascii=False)   
    
