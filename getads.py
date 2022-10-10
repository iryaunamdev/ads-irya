"""
Script for find IRyA publications from ADS database
search by affiliation/author/orcid and years period range
"""
from datetime import datetime
import sys
import json
import ads
import html
import re
import os
from unidecode import unidecode

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

def fuzzy(s, squeeze=True):
    """Transform string for a fuzzy comparison

    1. Decode HTML entities: "&amp;" -> "&"
    2. Eliminate accents: "Astrofísica" -> "Astrofisica"
    3. Fold case: "Astrofísica" -> "astrofisica"
    4. If optional argument `squeeze` is True, then remove
       non-word characters: "onom&ia y astro" -> "onomiayastro"
    """
    rslt = unidecode(html.unescape(s)).casefold()
    if squeeze:
        rslt = re.sub(r"\W", "", rslt)
    return rslt

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

def search_query(SEARCH_MODE, OPTIONS, Y_START, Y_END):
    if "R" in OPTIONS.split("="):
        search_options = " AND property:refereed"
                   
    year=''
    if "--aff" in SEARCH_MODE:
        print(SEARCH_MODE, end=" ")
        search_mode = SEARCH_MODE.replace('--', '')
        filename = year
        affstring = "(" + " OR ".join([f'"{_}"' for _ in aff_variants]) + ")"
        affstring2 = "(" + " OR ".join(unam_variants) + ")"
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
        
    elif "--author" in SEARCH_MODE:
        search_mode = SEARCH_MODE.split('=')[0].replace('--', '')
        print(SEARCH_MODE, end=" ")
        print(AUTHOR_ID, end=" ")
        author = SEARCH_MODE.split('=')[1]
        filename = str(year)+'_'+fuzzy(author)
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

    elif "--orcid" in SEARCH_MODE:
        print(SEARCH_MODE, end=" ")
        search_mode = SEARCH_MODE.split('=')[0].replace('--', '')
        orcid = SEARCH_MODE.split('=')[1]
        print(AUTHOR_ID, end=" ")
        filename = str(year)+'_'+orcid
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
    AUTHOR_ID = 0
    Y_START = 0
    Y_END = 0
    OUTPUT_DIR ="data"
    
    for arg in sys.argv:
        if arg.split("=")[0] == "--opt":
            OPTIONS = arg            
   
    for arg in sys.argv:
        if arg.split("=")[0] == "--aff" or  arg.split("=")[0] == "--author" or  arg.split("=")[0] == "--orcid":
            SEARCH_MODE = arg
        
    for arg in sys.argv:
        if arg.split("=")[0] == "--id":
            AUTHOR_ID = arg.split("=")[1]      
    
    for arg in sys.argv:
        if arg.split("=")[0] == "--start":
            Y_START = int(arg.split("=")[1])
        
    for arg in sys.argv:
        if arg.split("=")[0] == "--end":
            Y_END = int(arg.split("=")[1])
    
    for arg in sys.argv:
        if arg.split("=")[0] == "--output_dir":
            OUTPUT_DIR = arg.split("=")[1]             
         
    if Y_START and Y_END:
        if Y_END < Y_START:
            sys.exit(f"[Y_START] should before [Y_END]")   
            
    print(f"Año: {Y_START}-{Y_END}", end=" ")
    search_mode, filename,  papers = search_query(SEARCH_MODE, OPTIONS, Y_START, Y_END)
    print("Found:", len(papers), end=" ")
    papers_json = papers2JSON(papers)

    if len(papers):
        isExist = os.path.exists(OUTPUT_DIR+'/'+search_mode)

    if not isExist:  
        os.makedirs(OUTPUT_DIR+'/'+search_mode)
                    
    print("Saving JSON file...", end=" ")
    #generate JSON files
    with open(f"{OUTPUT_DIR}/{search_mode}/{AUTHOR_ID}_{filename}.json", "w+", encoding='utf-8') as outfile:
        json.dump(papers_json, outfile, ensure_ascii=False)
    print("Finish", end="\n")
    
    