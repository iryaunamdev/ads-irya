import sys
import ads
import os
import adsfunctions

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
        papersJSON[paper.bibcode] = dict_row
    return papersJSON


def search_query_aff(year, search_options):
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
    return papers
        
def search_query_author(author, year, search_options):
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
    return papers

def search_query_orcid(orcid, year, search_options):
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
                rows=2000,
                sort="date+desc",
            )
        )
    return papers

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

SEARCH_MODE = ""
OPTIONS = ""
Y_START = 0
Y_END = 0
WORKDIR = ""

for arg in sys.argv:
    if "--aff" in arg or "--author" in arg or "--orcid" in arg:
        SEARCH_MODE = arg
    elif "--workdir" in arg:
        WORKDIR = arg.split("=")[1]
    elif "--opt" in arg:
        OPTIONS = arg.split('=')[1]
        OPTIONS = OPTIONS.split()
    elif "--start" in arg:
        Y_START = arg.split("=")[1]
    elif "--end" in arg:
        Y_END = arg.split("=")[1]
        
if SEARCH_MODE == "" or WORKDIR=="":
        sys.exit("ERROR: WORKDIR or SEARCH_MODE necessary")             
if Y_END < Y_START:
        sys.exit(f"[Y_START] should before [Y_END]")
        
search_options = ""
if "R" in OPTIONS:
    search_options = " AND property:refereed"
papers = {}       
for year in range(Y_START, Y_END+1):
    print(SEARCH_MODE, end=" ")
    if '--aff' in SEARCH_MODE:
        papers =  search_query_aff(year, search_options)
        filename = f"{year}_irya"
    elif '--author' in SEARCH_MODE:
        SEARCH_MODE, author = SEARCH_MODE.split("=")
        if author:
            papers=search_query_author(author, year, search_options)
            filename = f"{year}_{adsfunctions.fuzzy(author)}"
    elif '--orcid' in SEARCH_MODE:
        SEARCH_MODE, orcid = SEARCH_MODE.split("=")
        if orcid:
            papers=search_query_orcid(orcid, year, search_options)
            filename = f"{year}_{orcid}"
    
    print("Found:", len(papers), end=" ")
    if len(papers): 
        papers_json = papers2JSON(papers)
        
        isExist = os.path.exists(f"{WORKDIR}/{SEARCH_MODE.replace('--', '')}")
        if not isExist:  
            os.makedirs(f"{WORKDIR}/{SEARCH_MODE.replace('--', '')}")
        
        print("Saving JSON file...", end=" ")
        adsfunctions.writeJSON(papers_json, f"{WORKDIR}/{SEARCH_MODE.replace('--', '')}/{filename}.json")
    print("Finish", end="\n")