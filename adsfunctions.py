import html
import re
import json
from fuzzywuzzy import process
from unidecode import unidecode

def markAuthor(authors, author_match):
    for i, author in enumerate(authors):
        if author_match in author:
            return i
    return -1   

def evaluation(paper, data, aff_variants):
    eval = {}
    eval['orcid_user'] = paper['orcid_user']
    eval['author'] = paper['author']
    eval['aff'] = paper['aff']
    eval['match_author'] = process.extractOne(data['author'], paper['author'])
    if data['orcid']:
        eval['match_orcid'] = process.extractOne(data['orcid'], paper['orcid_user'])
    else:
        eval['match_orcid'] = ()
    matched_orcid = matchOrcid(eval['match_orcid'])
    matched_author = matchAuthor(eval['match_author'][1], data['umbral'], data['umbral_descarte'])
    matched_aff = matchAff(paper, aff_variants)
    eval['evaluation'] = (matched_orcid, matched_author, matched_aff)
    if matched_aff or matched_orcid or matched_author:
        return True, eval
    else:
        return False, eval
    
def readJSON(FILENAME):
    with open(FILENAME, 'r') as json_file:
        return json.load(json_file)

def writeJSON(data, FILENAME):
    with open(FILENAME, "w+", encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False)
    
def matchAff(paper, aff_variants):
    for aff in paper['aff']:
        for variant in aff_variants:
            if variant in aff:
                return True
    return False

def matchOrcid(match_value):
    if match_value == 100:
        return True
    return False

def matchAuthor(match_value, umbral, descarte):
    if match_value in range(umbral, 101) and match_value not in descarte:
        return True
    return False

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