import json

with open('data/consolidate_papers.json') as json_file:
    papers_all = json.load(json_file)
        
with open('data/irya.list.json') as json_file_data:
    author_data = json.load(json_file_data)
    
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
    
papers_confirm ={}
papers_descarted = {}
for author_id, papers in papers_all.items():
    umbral = author_data[author_id]['umbral']
    umbral_descarte = author_data[author_id]['umbral_descarte']
    papers_author_confirm = {}
    papers_author_descarted = {}    
    for bibcode, paper in papers.items():
        if confirmOrcid(paper)[1] or confirmAuthor(paper, umbral, umbral_descarte)[1] or confirmAff(paper)[1]:
            paper['evaluation'] = [confirmOrcid(paper), confirmAuthor(paper, umbral, umbral_descarte), confirmAff(paper)]
            papers_author_confirm[bibcode] = paper
        else:
            papers_author_descarted[bibcode]=paper
            print(author_data[author_id]['id'], bibcode, confirmOrcid(paper), confirmAuthor(paper, umbral, umbral_descarte),  confirmAff(paper), paper['match_author'], paper['author'], paper['aff'])
        
    papers_confirm[author_id] = papers_author_confirm
    papers_descarted[author_id] = papers_author_descarted

with open("data/confirmed_papers.json", "w", encoding='utf-8') as outfile:
    json.dump(papers_confirm, outfile, ensure_ascii=False) 
with open("data/depurated_papers.json", "w", encoding='utf-8') as outfile:
    json.dump(papers_descarted, outfile, ensure_ascii=False)