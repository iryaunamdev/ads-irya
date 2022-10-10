while IFS="|" read id orcid author extra; do 
    python3 getads.py --author="$author" --id="$id" --start=1960 --end=2022 --output_dir="data/$(date +"%Y%m%d")"
    python3 getads.py --orcid="$orcid" --id="$id" --start=1960 --end=2022 --output_dir="data/$(date +"%Y%m%d")"
done < data/irya.list