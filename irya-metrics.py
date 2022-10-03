import json
import sys

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

papersA = {}
papersO = {}
papersAll = {}

for author in author_list:
    author = author.split('|')
    print(author)
    with open('data/author_'+author[0]+'.json') as json_file:
        papersA = json.load(json_file)
    if author[1]:
        with open('data/orcid_'+author[0]+'.json') as json_file:
            papersO = json.load(json_file)
        papersAll = consolidatePapers(papersA, papersO)
    else:
        papersAll = papersA 
    
    for bibcode, paper in papersAll.items():
        print(bibcode, paper['match_orcid'])
    
