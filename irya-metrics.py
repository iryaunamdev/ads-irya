import json
import sys
import pandas as pd

"""
Script for generate metrics by author (total_articles, citations, normalized_citations, h-index)
into a json and txt file
"""

AUTHOR_LIST = sys.argv[1]
author_list_file = open(AUTHOR_LIST, 'r')
author_list = author_list_file.read().split('\n')

data_metrics = []

for author in author_list:
    author = author.split('|')
    with open('data/'+author[0]+'.json') as json_file:
        papers = json.load(json_file)
    
    row_metrics = {}
    t_art = 0
    t_art_ref = 0
    t_citas = 0
    t_citas_norm = 0
    h_index = 0
    cites_list = []
    for bibcode, paper in papers.items():
      if 'NOT REFEREED' not in paper['property']:
          t_art += 1 
          t_citas += paper['citation_count']
          t_authors = len(paper['author'])
          cita_norm = paper['citation_count']/t_authors
          t_citas_norm += cita_norm 
          cites_list.append(int(paper['citation_count']))
          h_index = gethindex(cites_list)

