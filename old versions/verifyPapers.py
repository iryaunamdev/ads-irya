import json

with open('data/consolidate_papers.json') as json_file:
    papers_all = json.load(json_file)
    
for author_id, papers_data in papers_all.items():
    for bibcode, paper in papers_data.items():
        print(author_id, bibcode, paper['match_author'], paper['author'] )