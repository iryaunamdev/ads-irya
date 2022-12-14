from random import choices
import sys
import ads
import json
import re
import html
import csv
from datetime import datetime
from fuzzywuzzy import process
from unidecode import unidecode

ads.config.token ="LaMEJM2RdjlrmUgl3m7G5brYVmW7vHB243uAfS9j"
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

papersByAuthor = []
papersByOrcid =[]
papersAll =[]

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

def query_author(author:str)->list:
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

def query_orcid(orcid:str)->list:
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

def papers2CSV(dataArray, author_id):
    data = []
    for paper in dataArray:
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
        choices = paper.author
        author_match_score = process.extractOne(author[2], choices)
        values.append(author_match_score)
                
        choices = paper.orcid_user
        orcid_match_score = process.extractOne(author[1], choices)
        values.append(orcid_match_score)
        
        data.append(values)
        
    fields.append('author_match')
    fields.append('orcid_match')
    
    return fields, data
    
def papers2JSON(dataArray, filename):
    papersJSON = {}
    for paper in dataArray:
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
        
        choices = paper.author
        author_match_score = process.extractOne(author[2], choices)
        dict_row['match_author'] = author_match_score
        
        choices = paper.orcid_user
        orcid_match_score = process.extractOne(author[1], choices)
        dict_row['match_orcid'] = orcid_match_score
        
        papersJSON[paper.bibcode] = dict_row
        
    return papersJSON
    
if __name__=="__main__":
    try:
        AUTHOR_LIST_FILE = sys.argv[1]
    except IndexError:
        sys.exit(f"Usage: {sys.argv[0]} AUTHOR [Y_START] [Y_END]")
        
    try:
        Y_START = sys.argv[2]
    except IndexError:
        Y_START = datetime.today().year
        
    try:
        Y_START = sys.argv[3]
    except IndexError:
        Y_START = datetime.today().year
        
    author_list_file = open(AUTHOR_LIST_FILE, 'r')
    author_list = author_list_file.read().split('\n')
    for author in author_list:
        
        print(author, end=" ")
        author = author.split('|')
        
        #Get papers search
        papersByAuthor= query_author(fuzzy(author[2], squeeze=False))
        print("papersByAuthor: ", len(papersByAuthor), end=" ")
        papers_json_author = papers2JSON(papersByAuthor, "author_"+author[0])
        papers_csv_author = papers2CSV(papersByAuthor, "author_"+author[0])
        if author[1]:
            papersByOrcid =query_orcid(author[1])
            print("papersByOrcid: ", len(papersByOrcid), end=" ")
            papers_json_orcid = papers2JSON(papersByOrcid, "orcid_"+author[0])
            papers_csv_orcid = papers2CSV(papersByOrcid, "orcid_"+author[0])
           
        print()
        #generate JSON files
        with open('data/author/'+author[0]+".json", "w", encoding='utf-8') as outfile:
            json.dump(papers_json_author, outfile, ensure_ascii=False)
        with open('data/orcid/'+author[0]+".json", "w", encoding='utf-8') as outfile:
            json.dump(papers_json_orcid, outfile, ensure_ascii=False)
        
        #generate TSV files
        with open('data/author/'+author[0]+'.tsv', 'w', encoding='UTF8') as file:
            dw = csv.writer(file, delimiter='\t')
            dw.writerow(papers_csv_author[0])
            dw.writerows(papers_csv_author[1])
        with open('data/orcid/'+author[0]+'.tsv', 'w', encoding='UTF8') as file:
            dw = csv.writer(file, delimiter='\t')
            dw.writerow(papers_csv_orcid[0])
            dw.writerows(papers_csv_orcid[1])