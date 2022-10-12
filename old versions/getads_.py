"""
Script for find IRyA publications from ADS database
search by affiliation/author/orcid and years period range
"""
from datetime import datetime
import sys
import json
import ads
import os
from unidecode import unidecode
import adsfunctions

ads.config.token  = "LaMEJM2RdjlrmUgl3m7G5brYVmW7vHB243uAfS9j"

# Fields to retrive from ADS query
fields = [
    "bibcode",
    "title",
    "author",
    "aff",
    "aff_id",
    "year",
    "pub",
    "volume",
    "page",
    "pubdate",
    "date",
    "bibstem",
    "citation",
    "citation_count",
    "doctype",
    "orcid_user",
    "property",
    "keyword_norm" 
]

#Variants for affiliation
aff_variants = [
    "CRyA",
    "IRyA",
    "Radioastronomía y Astrofísica",
    "Radiostronomía y Astrofísica",  # Ricardo Gonzalez paper
    "Radioastronomí a y Astrofí sica",  # For Gustavo Bruzual 2021 paper
    "Radioastronomía y Astrofísca",  # Stan paper
    "Radioastronomía y Astrofsica",  # In anticipapation
    "Radioastromomía y Astrofísica",  # Just in case
]
unam_variants = [
    "UNAM",
    "Mexico",
    "Morelia",
]

def papers2JSON(papers):
    papersJSON = {}
    for paper in papers:
        values = [
                paper.bibcode,
                paper.title,
                paper.author,
                paper.aff,
                paper.aff_id,
                paper.year,
                paper.pub,
                paper.volume,
                paper.page,
                paper.pubdate,
                paper.date,
                paper.bibstem,
                paper.citation,
                paper.citation_count,
                paper.doctype,
                paper.orcid_user,
                paper.property,
                paper.keyword_norm      
            ]
        
        dict_row = dict(zip(fields, values))
        """
        choices = paper.author
        author_match_score = process.extractOne(author[2], choices)
        dict_row['match_author'] = author_match_score
        
        choices = paper.orcid_user
        orcid_match_score = process.extractOne(author[1], choices)
        dict_row['match_orcid'] = orcid_match_score
        """
        papersJSON[paper.bibcode] = dict_row
        
    return papersJSON

def search_query(SEARCH_MODE, OPTIONS, year):
    search_mode = ""
    filename = ""
    papers = {}
    
    if "R" in OPTIONS.split("="):
        search_options = " AND property:refereed"
        
    if "--aff" in SEARCH_MODE:
        print(SEARCH_MODE, end=" ")
        search_mode = SEARCH_MODE.replace('--', '')
        filename = f"irya_{year}"
        affstring = "(" + " OR ".join([f'"{_}"' for _ in aff_variants]) + ")"
        affstring2 = "(" + " OR ".join(unam_variants) + ")"
        if year:
            papers = list(
                ads.SearchQuery(
                    q=f"aff:{affstring}",
                    fq=f"aff:{affstring2}"+search_options,
                    database=f"astronomy",
                    fl=fields,
                    year=f"{year}",
                    rows=2000,
                    sort="date+desc",
                )
            )
        else:
            papers = list(
                ads.SearchQuery(
                    q=f"aff:{affstring}",
                    fq=f"aff:{affstring2}"+search_options,
                    database=f"astronomy",
                    fl=fields,
                    rows=2000,
                    sort="date+desc",
                )
            )             
        
    elif "--author" in SEARCH_MODE:
        search_mode = SEARCH_MODE.split('=')[0].replace('--', '')
        print(SEARCH_MODE, end=" ")
        print(AUTHOR_ID, end=" ")
        author = SEARCH_MODE.split('=')[1]
        if author:
            filename = str(year)+'_'+adsfunctions.fuzzy(author)
            if year:
                papers = list(
                    ads.SearchQuery(
                        q=f"author:{author}",
                        database=f"astronomy",
                        fl=fields,
                        year=f"{year}",
                        rows=2000,
                        sort="date+desc",
                    )
                )
            else:
                papers = list(
                    ads.SearchQuery(
                        q=f"author:{author}",
                        database=f"astronomy",
                        fl=fields,
                        rows=2000,
                        sort="date+desc",
                    )
                )

    elif "--orcid" in SEARCH_MODE:
        print(SEARCH_MODE, end=" ")
        search_mode = SEARCH_MODE.split('=')[0].replace('--', '')
        orcid = SEARCH_MODE.split('=')[1]
        if orcid:
            print(AUTHOR_ID, end=" ")
            filename = str(year)+'_'+orcid
            if year:
                papers = list(
                    ads.SearchQuery(
                        q=f"orcid:{orcid}",
                        database=f"astronomy",
                        fl=fields,
                        year=f"{year}",
                        rows=2000,
                        sort="date+desc",
                    )
                )
            else:
                papers = list(
                    ads.SearchQuery(
                        q=f"orcid:{orcid}",
                        database=f"astronomy",
                        fl=fields,
                        year=f"{year}",
                        rows=2000,
                        sort="date+desc",
                    )
                )
        return search_mode, filename, papers
    

if __name__=="__main__":
    OPTIONS=""
    SEARCH_MODE = ""
    AUTHOR_ID = ""
    Y_START = 0
    Y_END = 0
    WORKDIR ="data"
    
    for arg in sys.argv:
        if "--opt" in arg:
            OPTIONS = arg            
        elif "--aff" in arg or "--author" in arg or "--orcid" in arg:
            SEARCH_MODE = arg
        elif "--id" in arg:
            AUTHOR_ID = arg.split("=")[1]      
        elif "--start" in arg:
            Y_START = int(arg.split("=")[1])
        elif "--end" in arg:
            Y_END = int(arg.split("=")[1])
        elif "--workdir" in arg:
            WORKDIR = arg.split("=")[1]             
    
    if SEARCH_MODE == "" or WORKDIR=="":
        sys.exit("ERROR: WORKDIR or SEARCH_MODE necessary")             
    if Y_END < Y_START:
            sys.exit(f"[Y_START] should before [Y_END]")   
        
    for year in range(Y_START, Y_END+1):  
        print(f"Año: {Y_START}-{Y_END}", end=" ")
        search_mode, filename,  papers = search_query(SEARCH_MODE, OPTIONS, year)
        print("Found:", len(papers), end=" ")
        if len(papers):
            papers_json = papers2JSON(papers)
            print("Saving JSON file...", end=" ")
            adsfunctions.writeJSON(papers_json, f"{WORKDIR}/{search_mode}/{filename}.json")
            #isExist = os.path.exists(WORKDIR+'/'+search_mode)
        #if not isExist:  
            #os.makedirs(WORKDIR+'/'+search_mode)
        print("Finish", end="\n")   