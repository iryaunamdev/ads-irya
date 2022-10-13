# Script for consolidate ADS searches by autor/orcid or affiliation.
# This script generaates one new JSON file and (evaluation, depurated, events) log files.
# * The unique JSON file is formatted for SIIAA.
# ?
# !
# TODO

"""command usage
should especificate S_MODE (author/aff) and especificates the workdir
python consolidate.py [--author] [--aff] --workdir=WORKDIR
"""

import sys
import os
import adsfunctions

WORKDIR = ""
S_MODE = ""
REFERENCE_FILE = "data/irya.list.json"
EVALUATION_FILE = "evaluation_papers.json"
EVALUATION_LOG_FILE = "evaluation.log"
DEPURATED_LOG_FILE = "depurated.log"
EVENTS_LOG_FILE = "consolidated_events.log"
CONSOLIDATE_FILE = "irya_papers.json"
DESCARTED_FILE = "descarted.json"

# Extract args into vars
for arg in sys.argv[1::]:
    if "--workdir" in arg:
        WORKDIR = arg.split("=")[1]
    elif '--author' in arg:
        S_MODE = arg
    elif '--aff' in arg:
        S_MODE = arg

#comprobate WORKDIR and S_MODE defined from args
if WORKDIR == "" or S_MODE == "":
    sys.exit(f"Usage: {sys.argv[0]} [--aff] [--author] --workdir=WORKDIR")

#define log variables    
depurated_log = open(f"{WORKDIR}/{DEPURATED_LOG_FILE}", 'w+')
events_log = open(f"{WORKDIR}/{EVENTS_LOG_FILE}", 'w+')
evaluation_log = open(f"{WORKDIR}/{EVALUATION_LOG_FILE}", 'w+')

author_list = adsfunctions.readJSON(REFERENCE_FILE)
    
consolidated_papers = {}
descarted_papers    = {}
evaluation_papers   = {}
if S_MODE == "--author":
    for id, data in author_list.items():
        depurated_log.write(f"{data['author']}\n")
        evaluated_papers_author = {}
        
        #Read everyfile in WORKDIR/author
        for filename in os.listdir(f"{WORKDIR}/author"):
            #read files by author group
            if adsfunctions.fuzzy(data['author']) in filename:
                papers_author = adsfunctions.readJSON(f"{WORKDIR}/author/{filename}")
                for bibcode, paper in papers_author.items():
                    _is, evaluated_paper = adsfunctions.evaluation(paper, data)
                    evaluated_papers_author[bibcode] = evaluated_paper
                    
                    #if paper is evaluated and passed then add
                    if _is:                            
                        #save paper in consolidated_papers
                        if not bibcode in consolidated_papers.keys():
                            consolidated_papers[bibcode] = paper
                        
                        #Create keys if not exists
                        if 'author_siiaa' not in consolidated_papers[bibcode].keys():
                            consolidated_papers[bibcode]['author_siiaa'] = []
                        if 'author_mark' not in consolidated_papers[bibcode].keys():
                            consolidated_papers[bibcode]['author_mark'] = []   
                            
                        #add id for siiaa user owners
                        if int(id) not in consolidated_papers[bibcode]['author_siiaa']:
                            consolidated_papers[bibcode]['author_siiaa'].append(int(id))
                        
                        #add index for local authors to be marked in strong
                        mark_id = adsfunctions.markAuthor(paper['author'], evaluated_paper['match_author'][0])
                        if mark_id >= 0 and mark_id not in consolidated_papers[bibcode]['author_mark']:
                            consolidated_papers[bibcode]['author_mark'].append(mark_id)
                        
                        evaluation_log.write(f"{id}\t\t{bibcode}\t{evaluated_paper['evaluation']}\t{evaluated_paper['match_author']}\t{evaluated_paper['author']}\t{evaluated_paper['match_orcid']}\t{evaluated_paper['orcid_user']}\t{evaluated_paper['aff']}\n")
                    
                    #if paper is dismissed then
                    else:
                        if not bibcode in descarted_papers.keys():
                            descarted_papers[bibcode] = paper
                        evaluation_log.write(f"{id}\t-\t{bibcode}\t{evaluated_paper['evaluation']}\t{evaluated_paper['match_author']}\t{evaluated_paper['author']}\t{evaluated_paper['match_orcid']}\t{evaluated_paper['orcid_user']}\t{evaluated_paper['aff']}\n")
                        depurated_log.write(f"  -{bibcode} {evaluated_paper['evaluation']} {evaluated_paper['match_orcid']} {evaluated_paper['match_author']}")
        
        #Read everyfile in WORKDIR/orcid
        for filename in os.listdir(f"{WORKDIR}/orcid"):
            #read files by author group
            if data['orcid'] and data['orcid'] in filename:
                papers_orcid = adsfunctions.readJSON(f"{WORKDIR}/orcid/{filename}")
                for bibcode, paper in papers_orcid.items():
                    _is, evaluated_paper = adsfunctions.evaluation(paper, data)
                    evaluated_papers_author[bibcode] = evaluated_paper
                    
                    #if paper is evaluated and passed then add
                    if _is:                            
                        #save paper in consolidated_papers
                        if not bibcode in consolidated_papers.keys():
                            consolidated_papers[bibcode] = paper
                            
                        #Create keys if not exists
                        if 'author_siiaa' not in consolidated_papers[bibcode].keys():
                            consolidated_papers[bibcode]['author_siiaa'] = []
                        if 'author_mark' not in consolidated_papers[bibcode].keys():
                            consolidated_papers[bibcode]['author_mark'] = []
                            
                        #add id for siiaa user owners
                        if int(id) not in consolidated_papers[bibcode]['author_siiaa']:
                            consolidated_papers[bibcode]['author_siiaa'].append(int(id))
                        
                        #add index for local authors to be marked in strong
                        print(evaluated_paper['match_author'])
                        mark_id = adsfunctions.markAuthor(paper['author'], evaluated_paper['match_author'][0])
                        if mark_id >= 0 and mark_id not in consolidated_papers[bibcode]['author_mark']:
                            consolidated_papers[bibcode]['author_mark'].append(mark_id)
                    
                    #if paper is dismissed then
                    else:
                        if not bibcode in descarted_papers.keys():
                            descarted_papers[bibcode] = paper
                        depurated_log.write(f"  -{bibcode} {evaluated_paper['evaluation']} {evaluated_paper['match_orcid']} {evaluated_paper['match_author']}\n")
        
        evaluation_papers[id] = evaluated_papers_author
    adsfunctions.writeJSON(evaluation_papers, f"{WORKDIR}/{EVALUATION_FILE}")
    adsfunctions.writeJSON(descarted_papers, f"{WORKDIR}/{DESCARTED_FILE}")
    adsfunctions.writeJSON(consolidated_papers, f"{WORKDIR}/{CONSOLIDATE_FILE}")
elif S_MODE == "--aff":
    #Read everyfile in WORKDIR/aff
    for filename in os.listdir(f"{WORKDIR}/aff"):
        papers_aff = adsfunctions.readJSON(f"{WORKDIR}/aff/{filename}")
        for bibcode, paper in papers_aff.items():
            #print(bibcode, )
            if not bibcode in consolidated_papers.keys():
                consolidated_papers[bibcode] = paper
                        
                #Create keys if not exists
                if 'author_siiaa' not in consolidated_papers[bibcode].keys():
                    consolidated_papers[bibcode]['author_siiaa'] = []
                if 'author_mark' not in consolidated_papers[bibcode].keys():
                    consolidated_papers[bibcode]['author_mark'] = []
                
                #Get aff author list
                aff_author_list = adsfunctions.markAuthorAff(paper)
                consolidated_papers[bibcode]['author_mark'] = aff_author_list
                
                #realation aff_author - siiaa user
                siiaa_authors = []
                for aff_author in aff_author_list:
                    author = adsfunctions.fuzzy(paper['author'][aff_author].split(',')[0], squeeze=False)
                    print(author)
                    for id, data in author_list.items():
                        surname = adsfunctions.fuzzy(data['author'].split(',')[0], squeeze=False)
                        if surname == author:
                            siiaa_authors.append(int(id))
                                            
                consolidated_papers[bibcode]['author_siiaa'] = siiaa_authors
    adsfunctions.writeJSON(consolidated_papers, f"{WORKDIR}/aff/{CONSOLIDATE_FILE}")                    
