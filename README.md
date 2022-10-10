# ads-irya
Script for discovery an work with ADS records


**getadsby.py**

for search by affiliation 
python getads.py --aff [-opt=R] [--start=2001] [--end=2003] [--output_dir=]

--opt=R #for sesrch only refereed papers
--start=year_start_search #if left blank 2003 for default
--end=year_end_search #if left blank present year for default

for search by author
python getads.py --author="Arthur, Sarha Jane" --id=4 [-opt=R] [--start=2001] [--end=2003]

--author=author_search #search string for author
--id=id_siia  #id for link with others systems

search by orcid
python getads.py --orcid="0000-0000-0000-0000" [-opt=R] [--start=2001] [--end=2003]

--orcid=orcid_id #search orcid string 
--id=id_siia  #id for link with others systems


**consolidatePapers.py**

**depuratPapers.py**
