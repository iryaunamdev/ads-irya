while IFS="|" read id orcid author extra; do 
    if [ -z "$author" ]
    then
        echo "No author value"
    else
        #python3 getads.py --author="$author" --id="$id" --start=2022 --end=2022 --output_dir="data/$(date +"%Y%m%d")"
        python3 getads.py --author="$author" --id="$id" --opt=R --workdir="data/$(date +"%Y%m%d")"
    fi

    if [ -z "$orcid" ]
    then
      echo "No ORCID value"
    else
      python3 getads.py --orcid="$orcid" --id="$id" --opt=R --workdir="data/$(date +"%Y%m%d")"
      #python3 getads.py --orcid="$orcid" --id="$id" --start=2022 --end=2022 --output_dir="data/$(date +"%Y%m%d")"
    fi 
done < data/irya.list