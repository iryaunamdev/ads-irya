"""
make_irya_publication_list.py

Creates the web page publication_list2.php, which contains lists of
refereed journal publications by members of the IRyA, organized by
year from 2003 to the present.  Also creates the web page
latest_publication2.php with the most recent paper.

Usage:

    make_irya_publication_list.py OUTPUT_FOLDER

Files will be written to OUTPUT_FOLDER

See accompanying file README.md for further options.

Authors: Will Henney and Jane Arthur, 2022
"""

# Standard library imports
import sys
import json
import datetime
import re
from textwrap import dedent
import html
import ads
from unidecode import unidecode

DIAGNOSTIC_FILE = "nonstandard_variants.txt"


# Add bibcodes to this list in order to inspect for debugging purposes
DEBUG_BIBCODES = [
    # "2020ApJ...905...25G",  # Failed highlighting in author list
    # "2007JKAS...40..137K",  # Stan paper with "&" in affiliation
]

# We look for these different variants of the institute name
#
# Any special cases due to journal errors should be added to the end
# of this list
irya_variants = [
    "CRyA",
    "IRyA",
    "Radioastronomía y Astrofísica",
    "Radiostronomía y Astrofísica",  # Ricardo Gonzalez paper
    "Radioastronomí a y Astrofí sica",  # For Gustavo Bruzual 2021 paper
    "Radioastronomía y Astrofísca",  # Stan paper
    "Radioastronomía y Astrofsica",  # In anticipapation
    "Radioastromomía y Astrofísica",  # Just in case
]

drop_authors_after_dates = [
    ("Rodriguez-Gomez", "2022/09"),
    # ("Henney", "2022/04"),
]

# All except the first 3 variants are mis-spellings, about which we
# may want to report diagnostics
nonstandard_variants = irya_variants[3:]

# List for saving papers that we find with nonstandard affiliation
nonstandard_papers = []

affstring = "(" + " OR ".join([f'"{_}"' for _ in irya_variants]) + ")"

# To eliminate false positives in Italy, we have an auxiliary check on UNAM or Morelia
unam_variants = [
    '"UNAM"',
    '"Mexico"',
    '"Morelia"',
]
affstring2 = "(" + " OR ".join(unam_variants) + ")"

# These are the fields that we want the ADS query to give us
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


def check_drop_author_on_date(author, date):
    """True if author is due to be dropped on given date"""
    for _author, _date in drop_authors_after_dates:
        if _author in author and date > _date:
            # Case that author should be dropped
            return True
    # Case that author should not be dropped
    return False


def mark_irya_affiliations(paper):
    """Highlight authors with IRyA affiliation

    This mutates the paper.author list, so should be called only once
    """
    year_month = "/".join(paper.pubdate.split("-")[:-1])
    n_marked = 0
    for i, [author, affil] in enumerate(zip(paper.author, paper.aff)):
        for variant in irya_variants:
            if fuzzy(variant) in fuzzy(affil):
                if check_drop_author_on_date(author, year_month):
                    print("Dropped author event: ", author)
                else:
                    paper.author[i] = f"<strong>{author}</strong>"
                    n_marked += 1
                # Stop checking variants. Advance to next author
                break
    return n_marked


def check_nonstandard_affiliations(paper):
    """Check for common mispellings with IRyA affiliation"""
    for i, [author, affil] in enumerate(zip(paper.author, paper.aff)):
        for variant in nonstandard_variants:
            if fuzzy(variant, squeeze=False) in fuzzy(affil, squeeze=False):
                nonstandard_papers.append([paper.bibcode, i, author, affil])
                break

def query_years(years):
    papers_all = {}
    for year in years:
        # Make a single ADS query for each year
        papers = list(
            ads.SearchQuery(
                q=f"aff:{affstring}",
                fq=f"aff:{affstring2} AND property:refereed",
                fl=fields,
                year=f"{year}",
                rows=2000,
                sort="date+desc",
            )
        )
        # Remove MNRAS early publication papers from list
        #papers = [_ for _ in papers if not ".tmp." in _.bibcode]

        
        # Add a list item for each paper
        for paper in papers:
            check_nonstandard_affiliations(paper)
            n_marked = mark_irya_affiliations(paper)

            if n_marked == 0:
                print("Paper not included due to all irya authors being on drop list")
                continue

            if paper.bibcode in DEBUG_BIBCODES:
                print("*** DEBUG_BIBCODE", paper.bibcode)
                print(paper.items())
        papers_all[year] = papers

    return papers_all


def dump_nonstandard():
    nauthors = len(nonstandard_papers)
    # Count unique bibcodes
    npapers = len(set([_[0] for _ in nonstandard_papers]))

    s = dedent(
        f"""\
        ############################################################
        # Non-standard spellings in IRyA affiliations 2003-present
        #
        # Total: {nauthors} authors in {npapers} papers
        ############################################################
        """
    )
    for bibcode, irank, author, affil in nonstandard_papers:
        s += dedent(
            f"""
            {bibcode}
            Author {irank + 1}: {author}
            Affil: {affil}
            """
        )
    with open(f"{OUTPUT_FOLDER}/{DIAGNOSTIC_FILE}", "w") as f:
        f.write(s)


if __name__ == "__main__":
    try:
        OUTPUT_FOLDER = sys.argv[1]
    except IndexError:
        sys.exit(f"Usage: {sys.argv[0]} OUTPUT_FOLDER [variant]")

    # Optionally write a file with the mispellings
    try:
        DO_SAVE_VARIANTS = "variant" in str(sys.argv[2])
    except IndexError:
        DO_SAVE_VARIANTS = False

    start_year = 2003
    this_year = datetime.date.today().year
    years = list(reversed(range(start_year, this_year + 1)))
    papers = query_years(years)
    papers_json = papers2JSON(papers)

    #generate JSON files
    with open(f"{OUTPUT_FOLDER}/{start_year}_{this_year}_papers_list.json", "w", encoding='utf-8') as outfile:
        json.dump(papers_json, outfile, ensure_ascii=False)
    
    if DO_SAVE_VARIANTS:
        dump_nonstandard()