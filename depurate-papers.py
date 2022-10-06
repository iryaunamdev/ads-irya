import json
import pandas as pd
from fuzzywuzzy import process

with open('data/papers_irya.json') as json_file:
        papers_all = json.load(json_file)
        
for author_id, papers in papers_all.items():
    for bibcode, paper in papers.items():
        print(author_id, bibcode, paper['match_orcid'], paper['match_author'], paper['author'], paper['keyword_norm'], sep="\t")