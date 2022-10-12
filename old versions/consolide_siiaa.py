"""
Consolidate all searches by author/orcid into one new JSON file    
"""

from dataclasses import replace
import sys
import os
import json
from getads import fuzzy
from fuzzywuzzy import process
from datetime import date

aff_variants = [
    "UNAM",
    "Mexico",
    "Morelia",
    "CRyA",
    "IRyA",
    "Radioastronomía y Astrofísica",
    "Radiostronomía y Astrofísica",  # Ricardo Gonzalez paper
    "Radioastronomí a y Astrofí sica",  # For Gustavo Bruzual 2021 paper
    "Radioastronomía y Astrofísca",  # Stan paper
    "Radioastronomía y Astrofsica",  # In anticipapation
    "Radioastromomía y Astrofísica",  # Just in case
]

def confirmAff(paper):
    for aff in paper['aff']:
        for variant in aff_variants:
            if variant in aff:
                return aff, True
    return "", False

def confirmOrcid(paper):
    if paper['match_orcid']:
        if paper['match_orcid'][1] == 100:
            return paper['match_orcid'][1], True
        else:
            return paper['match_orcid'][1], False
    return "", False

def confirmAuthor(paper, umbral, descarte):
    if paper['match_author']:
        match_author = paper['match_author'][1]
        if match_author in range(umbral, 101) and match_author not in descarte:
            return match_author, True
        else:
            return match_author, False
    return "", False

#Start main program
for args in sys.argv:
    for arg in sys.argv:
        if arg.split("=")[0] == "--workdir":
            print(arg) 
        else:
            sys.exit(f"ERR01 Usage: {sys.argv[0]} [--aff] [--author] --workdir=WORKDIR")
   

"""
for arg in sys.argv:
    if '--workdir' in arg: 
        WORKDIR = arg.split('=')[1]
    else:
        sys.exit(f"ERR01 Usage: {sys.argv[0]} [--aff] [--author] --workdir=WORKDIR")
    
    
    if '--aff' in arg:
        S_MODE = arg.replace('--', '')
    elif '--author' in arg:
        S_MODE = arg.replace('--', '')
    else:
        sys.exit(f"ERR02 Usage: {sys.argv[0]} [--aff] [--author] --workdir=WORKDIR")
        
REFERENCE_FILE = "data/irya.list.json"

with open(REFERENCE_FILE) as json_file:
    author_list = json.load(json_file)
    
#Read everyfile in WORKDIR/author
papers = {}
descarted_papers = {}
for id, author in author_list.items():
    print(author['author'])
    papers_author = {}
    d_papers = {}
    surname = author['author'].split(',')[0]
    
    if 'author' == S_MODE:
        #Read everyfile in WORKDIR/author
        for filename in os.listdir(f"{WORKDIR}/author"):
            if fuzzy(author['author']) in filename:
                with open(f"{WORKDIR}/author/{filename}", 'r') as json_author_file:
                    papers_info = json.load(json_author_file)
                
                for bibcode, paper in papers_info.items():
                    paper['match_author'] = process.extractOne(author['author'], paper['author'])
                    if author['orcid']:
                        paper['match_orcid'] = process.extractOne(author['orcid'], paper['orcid_user'])
                    else:
                        paper['match_orcid'] = []
                    is_orcid = confirmOrcid(paper)
                    is_author = confirmAuthor(paper, author['umbral'], author['umbral_descarte'])
                    is_aff = confirmAff(paper)
                    paper['match_aff'] = is_aff
                    paper['evaluation'] = [is_orcid[1], is_author[1], is_aff[1]]
                    if is_orcid[1] or is_author[1] or is_aff[1]:
                        papers_author[bibcode] = paper
                    else:
                        d_papers[bibcode]=paper
                        print(f"    [*] {id} {bibcode} {is_orcid[1]} {is_aff} {is_author} {paper['match_author']}"  , paper['author'], paper['aff'])
            
        #Read everyfile in WORKDIR/orcid
        if author['orcid']:
            for filename in os.listdir(f"{WORKDIR}/orcid"):
                if author['orcid'] in filename:
                    with open(f"{WORKDIR}/orcid/{filename}", 'r') as json_author_file:
                        papers_info = json.load(json_author_file)

                    for bibcode, paper in papers_info.items():
                        if bibcode not in papers_author.keys():
                            paper['match_author'] = process.extractOne(author['author'], paper['author'])
                            if author['orcid']:
                                paper['match_orcid'] = process.extractOne(author['orcid'], paper['orcid_user'])
                            else:
                                paper['match_orcid'] = []
                                
                            is_orcid = confirmOrcid(paper)
                            is_author = confirmAuthor(paper, author['umbral'], author['umbral_descarte'])
                            is_aff = confirmAff(paper)
                            paper['match_aff'] = is_aff
                            paper['evaluation'] = [is_orcid[1], is_author[1], is_aff[1]]
                            
                            if is_orcid[1] or is_author[1] or is_aff[1]:
                                papers_author[bibcode] = paper
                            else:
                                d_papers[bibcode]=paper
                                print(f"    [*] {id} {bibcode} {is_orcid[1]} {is_aff} {is_author} {paper['match_author']}"  , paper['author'], paper['aff'])

        papers[id] = papers_author
        descarted_papers[id] = d_papers
        print(f" + Papers: {len(papers_author)} - Descarted: {len(d_papers)}")
        print()
    
if 'aff' == S_MODE:
     #Read everyfile in WORKDIR/aff
    for filename in os.listdir(f"{WORKDIR}/aff"):
        with open(f"{WORKDIR}/aff/{filename}", 'r') as json_aff_file:
            papers_info = json.load(json_aff_file)
            for bibcode, paper in papers_info.items():
                
                #Mark author with strong
                for i, [aff_author, affil] in enumerate(zip(paper.author, paper.aff)):
                    for variant in aff_variants:
                        if fuzzy(variant) in fuzzy(affil):
                            paper.author[i] = f"<strong>{author}</strong>"
                            for id, author in author_list.items():
                                print(fuzzy(author['author'].split(',')[1], squeeze=False))
                                #if fuzzy(author['author'].split(',')[1], squeeze=False)
                                 #   print()           
                        
                            
            
    
verify_log = open(f'{WORKDIR}/{S_MODE}_verify.log', 'w+')
for id, papers_author in papers.items():
    for bibcode, paper in papers_author.items():
        verify_log.write(f"{id} {bibcode} {paper['evaluation']} {paper['match_author']} {paper['author']} {paper['aff']}\n") 
        


with open(f"{WORKDIR}/{S_MODE}_papers.json", 'w+', encoding='utf-8') as outfile:
        json.dump(papers, outfile, ensure_ascii=False)
with open(f"{WORKDIR}/{S_MODE}_descarted.json", 'w+', encoding='utf-8') as outfile:
        json.dump(descarted_papers, outfile, ensure_ascii=False)
"""